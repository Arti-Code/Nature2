from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.life import Life
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor, PolySensor
from lib.net import Network
from lib.config import *


class Plant(Life):

    def __init__(self, screen: Surface, space: Space, sim: object, collision_tag: int, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color=None, color3=None, position: Vec2d=None):
        super().__init__(screen=screen, space=space, owner=sim, collision_tag=collision_tag, position=position)
        self.life_time = cfg.PLANT_LIFE
        self.size = size
        self.max_size = cfg.PLANT_MAX_SIZE
        self.max_energy = pow(cfg.PLANT_MAX_SIZE, 2)
        self.color0 = Color('yellowgreen')
        self.color1 = Color('green')
        self._color0 = Color('yellowgreen')
        self._color1 = Color('green')
        self.energy = pow(self.size, 2)
        self.generation = 0
        self.shape = Circle(self, self.size)
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        self.new_plant = 2

    def life_time_calc(self, dt: int):
        self.life_time -= dt
        if self.life_time <= 0:
            return True
        return False

    def update(self, dt: float):
        #if self.new_plant > 0:
        #    self.new_plant -= 1
        #    if self.new_plant==0:
        #        self.shape.collision_type=6
        if self.energy < self.max_energy and self.energy > 0:
            self.energy += cfg.PLANT_GROWTH*dt
            new_size = floor(sqrt(self.energy))
            if new_size != self.size:
                if new_size <= cfg.PLANT_MAX_SIZE:
                    self.shape.unsafe_set_radius(new_size)
                else:
                    self.shape.unsafe_set_radius(cfg.PLANT_MAX_SIZE)
        else:
            self.energy = self.max_energy
            self.size = self.max_size
        self.energy = clamp(self.energy, 0, self.max_energy)
        self.color0 = self._color0
        self.color1 = self._color1

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)

    def draw(self, screen: Surface, selected: Body):
        super().draw(screen, selected)
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r), self.color0)
        if r >= 3 and self.color1 != None:
            gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r-2), self.color1)
        #if r >= 6 and self.color3 != None:
        #    gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(2), self.color3)