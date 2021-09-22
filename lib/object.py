from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform, Shape
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor
from lib.net import Network
from lib.config import *

class Object(Body):
    def __init__(self, screen: Surface, space: Space, sim: object, collision_tag: int, world_size: Vec2d, shape: Shape, position: Vec2d=None, color0: Color=None, color1: Color=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.color0 = color0
        self.color1 = color1
        if position is not None:
            self.position = position
        else:
            x = randint(50, world_size[0]-50)
            y = randint(50, world_size[1]-50)
            self.position = Vec2d(x, y)
        self.shape = shape
        self.shape.collision_type = collision_tag
        space.add(self)
        space.add(self.shape)

    def update(self, dt: float):
        pass

    def draw(self):
        pass