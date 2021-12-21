# import standard PyTorch modules
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch import IntTensor
import torchvision
import torchvision.transforms as transforms
import numpy as np

# calculate train time, writing train data to files etc.
import time
import pandas as pd
import json
from IPython.display import clear_output, display
from PIL import Image


# Build the neural network, expand on top of nn.Module
class Network(nn.Module):
    def __init__(self):
        super().__init__()

        # define layers
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, kernel_size=(5, 5))
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=(5, 5))

        self.fc1 = nn.Linear(in_features=12 * 4 * 4, out_features=120)
        self.fc2 = nn.Linear(in_features=120, out_features=60)
        self.out = nn.Linear(in_features=60, out_features=10)

    # define forward function
    def forward(self, t):
        # conv 1
        t = self.conv1(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        # conv 2
        t = self.conv2(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        # fc1
        t = t.reshape(-1, 12 * 4 * 4)
        t = self.fc1(t)
        t = F.relu(t)

        # fc2
        t = self.fc2(t)
        t = F.relu(t)

        # output
        t = self.out(t)
        return t


def get_num_correct(preds, labels):
    return preds.argmax(dim=1).eq(labels).sum().item()


# import modules to build RunBuilder and RunManager helper classes
from collections import OrderedDict
from collections import namedtuple
from itertools import product


# Read in the hyper-parameters and return a Run namedtuple containing all the
# combinations of hyper-parameters
class RunBuilder():
    @staticmethod
    def get_runs(params):
        Run = namedtuple('Run', params.keys())

        runs = []
        for v in product(*params.values()):
            runs.append(Run(*v))

        return runs


# Helper class, help track loss, accuracy, epoch time, run time,
# hyper-parameters etc.
class RunManager():
    def __init__(self):
        # tracking every epoch count, loss, accuracy, time
        self.epoch_count = 0
        self.epoch_loss = 0
        self.epoch_num_correct = 0
        self.epoch_start_time = None

        # tracking every run count, run data, hyper-params used, time
        self.run_params = None
        self.run_count = 0
        self.run_data = []
        self.run_start_time = None

        # record model, loader and TensorBoard
        self.network = None
        self.loader = None

    # record the count, hyper-param, model, loader of each run
    # record sample images and network graph to TensorBoard
    def begin_run(self, run, network, loader):
        self.run_start_time = time.time()

        self.run_params = run
        self.run_count += 1

        self.network = network
        self.loader = loader

        images, labels = next(iter(self.loader))
        grid = torchvision.utils.make_grid(images)

    # when run ends, close TensorBoard, zero epoch count
    def end_run(self):
        self.epoch_count = 0

    # zero epoch count, loss, accuracy,
    def begin_epoch(self):
        self.epoch_start_time = time.time()

        self.epoch_count += 1
        self.epoch_loss = 0
        self.epoch_num_correct = 0

    #
    def end_epoch(self):
        # calculate epoch duration and run duration(accumulate)
        epoch_duration = time.time() - self.epoch_start_time
        run_duration = time.time() - self.run_start_time

        # record epoch loss and accuracy
        loss = self.epoch_loss / len(self.loader.dataset)
        accuracy = self.epoch_num_correct / len(self.loader.dataset)

        # Write into 'results' (OrderedDict) for all run related data
        results = OrderedDict()
        results["run"] = self.run_count
        results["epoch"] = self.epoch_count
        results["loss"] = loss
        results["accuracy"] = accuracy
        results["epoch duration"] = epoch_duration
        results["run duration"] = run_duration

        # Record hyper-params into 'results'
        for k, v in self.run_params._asdict().items(): results[k] = v
        self.run_data.append(results)
        df = pd.DataFrame.from_dict(self.run_data, orient='columns')

        # display epoch information and show progress
        clear_output(wait=True)
        display(df)

    # accumulate loss of batch into entire epoch loss
    def track_loss(self, loss):
        # multiply batch size so variety of batch sizes can be compared
        self.epoch_loss += loss.item() * self.loader.batch_size

    # accumulate number of corrects of batch into entire epoch num_correct
    def track_num_correct(self, preds, labels):
        self.epoch_num_correct += self._get_num_correct(preds, labels)

    @torch.no_grad()
    def _get_num_correct(self, preds, labels):
        return preds.argmax(dim=1).eq(labels).sum().item()

    # save end results of all runs into csv, json for further a
    def save(self, fileName):
        pd.DataFrame.from_dict(
            self.run_data,
            orient='columns',
        ).to_csv(f'{fileName}.csv')

        with open(f'{fileName}.json', 'w', encoding='utf-8') as f:
            json.dump(self.run_data, f, ensure_ascii=False, indent=4)


# helper function to calculate all predictions of train set
def get_all_preds(model, loader):
    all_preds = torch.tensor([])
    for batch in loader:
        images, labels = batch

        preds = model(images)
        all_preds = torch.cat(
            (all_preds, preds),
            dim=0
        )
    return all_preds


def inference(data):
    image = Image.fromarray(np.array(data['image'], dtype='uint8'))
    transform = transforms.Compose([transforms.ToTensor()])
    img_tensor = transform(image).unsqueeze_(0)
    network = Network()
    network.load_state_dict(torch.load('trained_model'))
    network.eval()
    with torch.no_grad():
        r = network.forward(img_tensor).argmax()
    return {'Predicted': IntTensor.item(r),
            'Ground_truth': data['label'],
            'Image Number': data['image number']}


def train(params, train_set, epochs, save_last_model=False, ):
    m = RunManager()

    # get all runs from params using RunBuilder class
    for run in RunBuilder.get_runs(params):

        # if params changes, following line of code should reflect the changes too
        network = Network()
        loader = torch.utils.data.DataLoader(train_set, batch_size=run.batch_size)
        optimizer = optim.Adam(network.parameters(), lr=run.lr)

        m.begin_run(run, network, loader)
        for epoch in range(epochs):

            m.begin_epoch()
            for batch in loader:
                images = batch[0]
                labels = batch[1]
                preds = network(images)
                loss = F.cross_entropy(preds, labels)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                m.track_loss(loss)
                m.track_num_correct(preds, labels)

            m.end_epoch()
        m.end_run()
        if save_last_model:
            torch.save(network.state_dict(), "trained_model")
    m.save('results')


if __name__ == '__main__':
    train_set = torchvision.datasets.FashionMNIST(
        root='./data/FashionMNIST',
        train=True,
        download=True,
        transform=transforms.Compose([
            transforms.ToTensor()
        ])
    )
    params = OrderedDict(
        lr=[.01, ],
        batch_size=[1000],
        shuffle=[True]
    )
    epochs = 150
    train(params, train_set, epochs, save_last_model=True)
