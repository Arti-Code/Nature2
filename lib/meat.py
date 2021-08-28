from math import sqrt, floor
from random import random, randint
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pymunk import Segment, Poly, Body, Circle, Space, Vec2d
from lib.math2 import flipy, clamp
from lib.config import *

class Meat(Body):

    def __init__(self, space: Space, position: Vec2d, collision_tag: int, radius: int, energy: int, color0: Color=Color('red'), color1: Color=Color('red4')):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.position = position
        self.energy = energy
        self.radius = floor(sqrt(self.energy)*0.25)
        self._color0 = color0
        self._color1 = color1
        self.color0 = color0
        self.color1 = color1
        self.time = cfg.MEAT_TIME
        self.shape = Circle(self, self.radius*1.5)
        self.shape.collision_type = collision_tag
        space.add(self, self.shape)
        #x = int(self.position.x); y = int(self.position.y)
        r = int(self.radius)
        self.circles = []
        if r >= 3:
            for m in range(0, r, 2):
                rx = randint(-5, 5)
                ry = randint(-5, 5)
                self.circles.append([rx, ry, m])
        else:
            self.circles.append(0, 0, 0)

    def draw(self, screen: Surface):
        x = int(self.position.x); y = int(self.position.y)
        r = int(self.radius)
        for rx, ry, m in self.circles:
            if r-m > 0:
                gfxdraw.filled_circle(screen, x+rx, flipy(y+ry), r-m+1, self.color1)
                gfxdraw.filled_circle(screen, x+rx, flipy(y+ry), r-m, self.color0)
            else:
                break
        #gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r), self.color1)
        #if r >= 3:
        #    for m in range(0, r, 2):
        #        rx = randint(-10, 10)
        #        ry = randint(-10, 10)
        #        gfxdraw.filled_circle(screen, x+rx, flipy(y+ry), r-m+1, self.color1)
        #        gfxdraw.filled_circle(screen, x+rx, flipy(y+ry), r-m, self.color0)
        #else:
        #    gfxdraw.filled_circle(screen, x, flipy(y), r, self.color1)

    def update(self, dT: float):
        self.time -= dT
        if self.time < 0:
            self.time = 0
        if self.energy < 0:
            self.energy = 0
        self._color0.a = round((255*self.time)/cfg.MEAT_TIME)
        self.color0 = self._color0
        new_size = floor(sqrt(self.energy)*0.25)
        if new_size != self.shape.radius:
            self.shape.unsafe_set_radius(new_size*1.5)

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)
