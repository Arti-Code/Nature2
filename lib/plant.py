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
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, world_size=world_size, size=3, color0=color0, color1=color1, color3=color3, position=position)
        self.life_time = PLANT_LIFE
        self.size = size
        self.max_size = PLANT_MAX_SIZE
        self.max_energy = pow(PLANT_MAX_SIZE, 2)
        self.color0 = Color('yellowgreen')
        self.color1 = Color('green')
        self.energy = 1
        self.generation = 0

    def life_time_calc(self, dt: int):
        self.life_time -= dt/1000
        if self.life_time <= 0:
            return True
        return False

    def update(self, dt: float):
        if self.energy < self.max_energy and self.energy > 0:
            self.energy += PLANT_GROWTH/dt
            new_size = floor(sqrt(self.energy))
            if new_size != self.size:
                if new_size <= PLANT_MAX_SIZE:
                    self.shape.unsafe_set_radius(new_size)
                else:
                    self.shape.unsafe_set_radius(PLANT_MAX_SIZE)
        else:
            self.energy = self.max_energy
            self.size = self.max_size
        self.energy = clamp(self.energy, 0, self.max_energy)
        return

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)

    def draw(self, screen: Surface, selected: Body):
        super().draw(screen, selected)