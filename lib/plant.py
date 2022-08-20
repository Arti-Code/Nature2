from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt, log2, log10
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly
from lib.life import Life
from lib.math2 import flipy, clamp
from lib.config import *
from lib.camera import Camera

class Plant(Life):

    def __init__(self, screen: Surface, space: Space, collision_tag: int, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color=None, color3=None, position: Vec2d=None):
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
        self.life_time = int(cfg.PLANT_LIFE*random() + cfg.PLANT_LIFE*random())
        self.size = size
        self.max_size = cfg.PLANT_MAX_SIZE
        self.max_energy = pow(2, cfg.PLANT_MAX_SIZE)
        self.color0 = Color('yellowgreen')
        self.color1 = Color('green')
        self._color0 = Color('yellowgreen')
        self._color1 = Color('green')
        self.energy = pow(2, self.size)
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

    def update(self, dt: float, selected: Body):
        super().update(dt, selected)
        if self.energy < self.max_energy and self.energy > 0:
            self.energy += cfg.PLANT_GROWTH*dt
            new_size = floor(log2(self.energy))
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

    def check_reproduction(self) -> bool:
        if self.energy >= self.max_energy:
            return True
        else:
            return False

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        x = self.position.x; y = flipy(self.position.y)
        r = ceil(self.shape.radius / camera.scale)
        rect = Rect(x-r, y-r, 2*r, 2*r)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        rx = rel_pos.x
        ry = rel_pos.y
        super().draw(screen, camera, selected)
        if r > 0:
            gfxdraw.filled_circle(screen, int(rx), int(ry), ceil(r), self.color0)
            if r > 2/camera.scale:
                gfxdraw.filled_circle(screen, int(rx), int(ry), ceil(r-2/camera.scale), self.color1)
        return True