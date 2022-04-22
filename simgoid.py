from turtle import color
from bokeh.io import show
from bokeh.plotting import figure, Figure
from lib.math2 import sigmoid, tanh, clamp
from math import sinh, sin, cos
from bokeh.colors import Color, RGB
from random import random

x_axe = list()
x_axe = [*range(0, 101, 1)]
y_axe1 = []
y_axe2 = []
ry_axe = []
rx_axe = []
for x in x_axe:
    y = (sigmoid(x/100)*2)-1
    y_axe1.append(y*0.5)
    y_axe2.append((1-y)*0.5)
    for _ in range(10):
        ry_axe.append(random())
        rx_axe.append(x)
print(f"RANGE: {x_axe}")
p = figure(plot_width=1000, plot_height=400)
p.line(x_axe, y_axe1, line_width=1, color=RGB(0, 0, 255))
p.line(x_axe, y_axe2, line_width=1, color=RGB(0, 255, 0))
p.dot(rx_axe, ry_axe, color=RGB(255, 0, 0))
show(p)