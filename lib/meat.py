from math import sqrt, floor, log2
from random import random, randint
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pymunk import Segment, Poly, Body, Circle, Space, Vec2d
from lib.math2 import flipy, clamp
from lib.life import Life
from lib.config import cfg
from pygame.math import Vector2
from lib.camera import Camera

class Meat(Life):

    def __init__(self, screen: Surface, space: Space, position: Vec2d, collision_tag: int, radius: int, energy: int, color0: Color=Color('red'), color1: Color=Color('red4')):
        #super().__init__(self, body_type=Body.KINEMATIC)
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
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

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        #super().draw(screen, selected)
        x = self.position.x; y = flipy(self.position.y)
        r = self.radius
        rect = Rect(x-r, y-r, 2*r, 2*r)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        rx = rel_pos.x
        ry = rel_pos.y
        super().draw(screen, camera, selected)
        if r > 0:
            gfxdraw.filled_circle(screen, int(rx), int(ry), int(r), self.color1)
            if r > 2:
                gfxdraw.filled_circle(screen, int(rx), int(ry), int(r-2), self.color0)
        return True

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
