from math import sin, cos, radians
import numpy as np


world = (600, 600)

def sort_by_fitness(record):
    return record['points']

def sort_by_water(record):
    return record.water

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def set_world(size: tuple):
    global world
    try:
        world = (int(size[0]), int(size[1]))
    except:
        world = (600, 600)
    finally:
        pass

def flipy(y):
    return -y + world[1]

def flipy2(y):
    return -y + 600

def ang2vec(radians: float) -> tuple:
    x = sin(radians); y = cos(radians)
    return (x, y)

def ang2vec2(radians: float) -> tuple:
    x = sin(radians); y = cos(radians)
    return (y, x)

def binary(x):
    if x > 0:
        return 1
    else:
        return 0

def rev_binary(x):
    if x >= 0:
        return 0
    else:
        return 1

def wide_binary(x):
    if x >= 0:
        return 1
    else:
        return -1

def linear(x):
    return min([max([-1, x]), 1])

def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))

def tanh(x):
    return np.tanh(x)
    
def relu(x):
    return np.maximum(0,x)

def leaky_relu(x):
    return np.maximum(0.1*x, x)