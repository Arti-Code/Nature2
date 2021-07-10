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

    def __init__(self, screen: Surface, space: Space, owner: object, collision_tag: int, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color=None, color3: Color=None, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.world_size = world_size
        self.max_energy = 200
        self.energy = self.max_energy
        #self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.base_color0 = copy(color0)
        self.base_color1 = copy(color1)
        if position is not None:
            self.position = position
        else:
            x = randint(50, world_size[0]-50)
            y = randint(50, world_size[1]-50)
            self.position = Vec2d(x, y)
        #if not angle:
        #    self.angle = random()*2*PI
        space.add(self)
        self.shape = Circle(body=self, radius=size, offset=(0, 0))
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        self.reproduction_time = REPRODUCTION_TIME
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False

    def draw(self, screen: Surface, selected: Body):
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r), self.color0)
        if r >= 3 and self.color1 != None:
            gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r-2), self.color1)
        if r >= 6 and self.color3 != None:
            gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(2), self.color3)
        if self == selected:
            self.draw_selection(screen, x, y, r)
        self.color0 = self.base_color0
        self.color1 = self.base_color1

    def update(self, dt: float):
        self.energy -= 1*dt*0.001
        if self.reproduction_time > 0:
            self.reproduction_time -= 1*dt*0.001

    def draw_selection(self, screen: Surface, x, y, r):
        gfxdraw.aacircle(screen, int(x), int(flipy(y)), int(r*2), Color('turquoise'))
        gfxdraw.aacircle(screen, int(x), int(flipy(y)), int(r*2+1), Color('turquoise'))

    


