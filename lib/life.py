from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.object import Object
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor, PolySensor
from lib.net import Network
from lib.config import *

class Life(Body):

    def __init__(self, screen: Surface, space: Space, owner: object, collision_tag: int, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        if position is not None:
            self.position = position
        else:
            x = randint(50, WORLD[0]-50)
            y = randint(50, WORLD[1]-50)
            self.position = Vec2d(x, y)
        space.add(self)
        
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False
        self.collide_meat = False

    def draw(self, screen: Surface, selected: Body):
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        if self == selected:
            self.draw_selection(screen, x, y, r)

    def update(self, dt: float):
        pass
    
    def draw_selection(self, screen: Surface, x, y, r):
        gfxdraw.aacircle(screen, int(x), int(flipy(y)), int(r*2), Color('turquoise'))
        gfxdraw.aacircle(screen, int(x), int(flipy(y)), int(r*2+1), Color('turquoise'))

    


