from math import sqrt, floor, log2
from random import random, randint
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pymunk import Segment, Poly, Body, Circle, Space, Vec2d
from lib.math2 import flipy, clamp
from lib.life import Life
from lib.config import cfg

class Meat(Life):

    def __init__(self, screen: Surface, space: Space, sim: object, position: Vec2d, collision_tag: int, radius: int, energy: int, color0: Color=Color('red'), color1: Color=Color('red4')):
        #super().__init__(self, body_type=Body.KINEMATIC)
        super().__init__(screen=screen, space=space, owner=sim, collision_tag=collision_tag, position=position)
        #self.position = position
        self.energy = energy
        self.radius = floor(log2(self.energy))
        self._color0 = color0
        self._color1 = color1
        self.color0 = color0
        self.color1 = color1
        self.time = cfg.MEAT_TIME
        self.shape = Circle(self, self.radius)
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        #x = int(self.position.x); y = int(self.position.y)
        r = int(self.radius)

    def draw(self, screen: Surface, selected: Body):
        super().draw(screen, selected)
        x = int(self.position.x); y = int(self.position.y)
        r = int(self.radius)
        if r > 0:
            gfxdraw.filled_circle(screen, x, flipy(y), r, self.color1)
            if r > 2:
                gfxdraw.filled_circle(screen, x, flipy(y), r-2, self.color0)

    def update(self, dT: float, selected: Body):
        super().update(dT, selected)
        self.time -= dT
        if self.time < 0:
            self.time = 0
        if self.energy < 0:
            self.energy = 0
        self._color0.a = round((255*self.time)/cfg.MEAT_TIME)
        self.color0 = self._color0
        if self.energy > 0:
            new_size = floor(log2(self.energy))
            if new_size != self.shape.radius:
                self.shape.unsafe_set_radius(new_size)
                self.radius = self.shape.radius

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)
