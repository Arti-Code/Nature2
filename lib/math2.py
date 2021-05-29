from math import sin, cos, radians

def flipy(y):
    return -y + 600

def ang2vec(radians: float) -> tuple:
    x = sin(radians); y = cos(radians)
    return (x, y)

def ang2vec2(radians: float) -> tuple:
    x = sin(radians); y = cos(radians)
    return (y, x)