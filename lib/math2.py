from math import sin, cos, radians

world = (600, 600)

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