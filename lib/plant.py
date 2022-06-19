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
        #self.area = Circle(self, cfg.PLANT_RANGE)
        #self.area.collision_type = 18
        #self.area.sensor = True
        #space.add(self.area)
        self.new_plant = 2
        self.plants_in_area = []
        self.area_timer = 5.0
        self.check_area: bool=False

    def life_time_calc(self, dt: int):
        self.life_time -= dt
        if self.life_time <= 0:
            return True
        return False

    def update(self, dt: float, selected: Body):
        super().update(dt, selected)
        #self.update_area_timer(dt=dt)
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

    def update_area_timer(self, dt: float, restart_time: float=5.0):
        self.area_timer -= dt
        if self.area_timer <= 0:
           # if not self.check_area:
            self.check_area = True
            #else:
                #self.check_area = False
                #self.area_timer = restart_time


    def check_reproduction(self) -> bool:
        if self.energy >= self.max_energy:
            return True
        else:
            return False

    def kill(self, space: Space):
        space.remove(self.shape)
        #space.remove(self.area)
        space.remove(self)

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        x = self.position.x; y = flipy(self.position.y)
        r = self.shape.radius
        rect = Rect(x-r, y-r, 2*r, 2*r)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        rx = rel_pos.x
        ry = rel_pos.y
        super().draw(screen, camera, selected)
        if r > 0:
            gfxdraw.filled_circle(screen, int(rx), int(ry), int(r), self.color0)
            if r >= 3 and self.color1 != None:
                gfxdraw.filled_circle(screen, int(rx), int(ry), int(r-2), self.color1)
        #if r >= 6 and self.color3 != None:
        #    gfxdraw.filled_circle(screen, int(rx), flipy(int(ry)), int(2), self.color3)
        return True