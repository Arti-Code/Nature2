from bokeh.colors import RGB
from bokeh.io import show
from bokeh.plotting import figure  #, Figure
from bokeh.layouts import gridplot 

from lib.config import cfg


class Statistics():

    def __init__(self):
        self.data = {}
        self.colors = {
            'plants': RGB(0, 255, 0),
            'herbivores': RGB(0, 0, 255),
            'carnivores': RGB(255, 0, 0),
            'all': RGB(100, 100, 100, 255),
            'size': RGB(0, 255, 0),
            'speed': RGB(0, 0, 255),
            'food': RGB(255, 0, 255),
            'power': RGB(255, 0, 0),
            'mutations': RGB(255, 255, 0),
            'vision': (135, 206, 250),
            'nodes': RGB(0, 255, 0),
            'links': RGB(0, 0, 255),
            'points': RGB(255, 0, 0, 255),
            'lifetime': RGB(0, 0, 255, 255)
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

    def load_statistics(self, collection_name: str, data: dict):
        self.data[collection_name] = data

    def plot(self):
        #data = self.data[collection_name]
        last = self.data['neuros']['time'][len(self.data['neuros']['time'])-1]
        x_range = (max(0, last-8000), max(last, last-4000))
        w = 1900
        #if int(data['time'][len(data['time'])-1]/10) > w:
        #    w = int(data['time'][len(data['time'])-1]/10)
        #if collection_name == 'creatures':
        y_range0 = (1, cfg.CREATURE_MAX_SIZE+1)
        p0=figure(width=w, height=250, y_range=y_range0, x_range=x_range)
        for data_key in self.data['creatures']:
            if data_key != 'time':
                d = self.data['creatures'][data_key]
                color = self.colors[data_key]
                p0.line(self.data['creatures']['time'], d, line_width=2, legend_label=data_key, color=color)
        p0.legend.location = "top_left"
        #elif collection_name == 'neuros':

        y_range1 = (0, max([max(self.data['neuros']['nodes']), max(self.data['neuros']['links'])])+5)
        p1=figure(width=w, height=250, y_range=y_range1, x_range=x_range)
        for data_key in self.data['neuros']:
            if data_key != 'time':
                d = self.data['neuros'][data_key]
                color = self.colors[data_key]
                p1.line(self.data['neuros']['time'], d, line_width=2, legend_label=data_key, color=color)
        p1.legend.location = "top_left"
        #elif collection_name == 'fitness':

        y_range2 = (0, max([max(self.data['fitness']['points']), max(self.data['fitness']['lifetime'])]))
        p2=figure(width=w, height=250, y_range=y_range2, x_range=x_range)
        for data_key in self.data['fitness']:
            if data_key != 'time':
                d = self.data['fitness'][data_key]
                color = self.colors[data_key]
                p2.line(self.data['fitness']['time'], d, line_width=2, legend_label=data_key, color=color)
        p2.legend.location = "top_left"
        #else:

        cr_num = max(self.data['populations']['all'])
        y_range3 = (0, max([cfg.PLANT_MAX_NUM, cr_num])+5)
        p3=figure(width=w, height=250, y_range=y_range3, x_range=x_range)
        for data_key in self.data['populations']:
            if data_key != 'time':
                d = self.data['populations'][data_key]
                color = self.colors[data_key]
                p3.line(self.data['populations']['time'], d, line_width=2, legend_label=data_key, color=color)
        p3.legend.location = "top_left"

        grid = gridplot([[p3], [p1], [p2], [p0]])
        show(grid) 


