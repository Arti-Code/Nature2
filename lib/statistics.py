from cProfile import label
from calendar import c
from matplotlib.image import FigureImage
from matplotlib.pyplot import legend
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure, Figure
from bokeh.layouts import column
from bokeh.colors import Color, RGB

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
        w = 1600
        if int(data['time'][len(data['time'])-1]/100) > w:
            w = int(data['time'][len(data['time'])-1]/100)
        p: Figure=figure(plot_width=w, plot_height=600)
        for data_key in data:
            if data_key != 'time':
                d = data[data_key]
                color = self.colors[data_key]
                p.line(data['time'], d, line_width=2, line_color=color)
        show(p)

    def plot4(self, collection_name: str):
        data = self.data[collection_name]
        w = 1600
        if int(data['time'][len(data['time'])-1]/100) > w:
            w = int(data['time'][len(data['time'])-1]/100)
        p: Figure=figure(plot_width=w, plot_height=600)
        for data_key in data:
            if data_key != 'time':
                d = data[data_key]
                color = RGB(0, 0, 0)
                if data_key == 'plants':
                    color = RGB(0, 255, 0)
                elif data_key == 'herbivores':
                    color = RGB(0, 0, 255)
                elif data_key == 'carnivores':
                    color = RGB(255, 0, 0)
                p.line(data['time'], d, line_width=2, line_color=color)
        show(p)

    def plot2(self, collection_name: str, colors: list, labels: list):
        data = self.data[collection_name]
        w = 1600
        if int(data['time'][len(data['time'])-1]/100) > w:
            w = int(data['time'][len(data['time'])-1]/100)
        p: Figure=figure(plot_width=w, plot_height=600)
        c = 0
        for data_key in data:
            if data_key != 'time':
                d = data[data_key]
                label = labels[c]
                color = colors[c]
                c += 1
                p.line(data['time'], d, line_width=2, line_color=color)
        p.legend = legend
        show(p)

    def plot3(self, collection_name: str):
        data = self.data[collection_name]
        w = 1600
        if int(data['time'][len(data['time'])-1]/100) > w:
            w = int(data['time'][len(data['time'])-1]/100)
        p1: Figure=figure(plot_width=w, plot_height=600)
        for data_key in data:
            if data_key != 'time':
                d1 = data[data_key]
                color = RGB(0, 0, 0)
                if data_key == 'plants':
                    color = RGB(0, 255, 0)
                elif data_key == 'herbivores':
                    color = RGB(0, 0, 255)
                elif data_key == 'carnivores':
                    color = RGB(255, 0, 0)
                p1.line(data['time'], d1, line_width=2, line_color=color)
        p2: Figure=figure(plot_width=w, plot_height=600)
        p2.line(data['time'], data['plants'], line_width=2, line_color=RGB(0, 255, 0))
        show(column(p1, p2))

    def load_statistics(self, collection_name: str, data: dict):
        self.data[collection_name] = data