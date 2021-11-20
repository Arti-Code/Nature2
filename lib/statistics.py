from calendar import c
from matplotlib.image import FigureImage
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure, Figure
from bokeh.colors import Color, RGB

class Statistics():

    def __init__(self):
        self.data = {}

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
        p: Figure=figure(plot_width=1600, plot_height=400)
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

    def load_statistics(self, collection_name: str, data: dict):
        self.data[collection_name] = data