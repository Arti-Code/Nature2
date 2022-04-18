from cProfile import label
from calendar import c
from matplotlib.image import FigureImage
from matplotlib.pyplot import legend
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure, Figure
from bokeh.layouts import column
from bokeh.colors import Color, RGB
from lib.config import cfg

class Statistics():

    def __init__(self):
        self.data = {}
        self.colors = {
            'plants': RGB(0, 255, 0),
            'herbivores': RGB(0, 0, 255),
            'carnivores': RGB(255, 0, 0),
            'size': RGB(0, 255, 0),
            'speed': RGB(0, 0, 255),
            'food': RGB(255, 0, 255),
            'power': RGB(255, 0, 0),
            'mutations': RGB(255, 255, 0),
            'nodes': RGB(0, 255, 0),
            'links': RGB(0, 0, 255)
        }

    def add_collection(self, collection_name: str, named_rows: list):
        collection = {}
        collection['time'] = []
        for row in named_rows:
            collection[row] = []
        self.data[collection_name] = collection

    def add_data(self, collection_name: str, time: int, data: dict):
        self.data[collection_name]['time'].append(time)
        for data_key in data:
            self.data[collection_name][data_key].append(data[data_key])

    def get_last_time(self, collection_name: str) -> int:
        l = len(self.data[collection_name]['time'])
        if l >= 1:
            return self.data[collection_name]['time'][l-1]
        else:
            return 0

    def get_collection(self, collection_name: str) -> dict:
        return self.data[collection_name]

    def plot(self, collection_name: str):
        data = self.data[collection_name]
        y_range1 = (1, cfg.CREATURE_MAX_SIZE+1)
        y_range2 = (0, cfg.PLANT_MAX_NUM+10)
        last = data['time'][len(data['time'])-1]
        x_range = (max(0, last-8000), max(last, last-4000))
        w = 1900
        #if int(data['time'][len(data['time'])-1]/10) > w:
        #    w = int(data['time'][len(data['time'])-1]/10)
        p: None
        if collection_name == 'creatures':
            p: Figure=figure(plot_width=w, plot_height=600, y_range=y_range1, x_range=x_range)
        elif collection_name == 'neuros':
            y_range3 = (0, max([max(self.data[collection_name]['nodes']), max(self.data[collection_name]['links'])])+5)
            p: Figure=figure(plot_width=w, plot_height=600, y_range=y_range3, x_range=x_range)
        else:
            p: Figure=figure(plot_width=w, plot_height=600, y_range=y_range2, x_range=x_range)
        for data_key in data:
            if data_key != 'time':
                d = data[data_key]
                color = self.colors[data_key]
                p.line(data['time'], d, line_width=2, legend_label=data_key, color=color)
        p.legend.location = "top_left"
        show(p)

    def load_statistics(self, collection_name: str, data: dict):
        self.data[collection_name] = data