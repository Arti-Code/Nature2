from math import ceil, floor, log2

import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface
from pygame.math import Vector2
from pymunk import Body, Circle, Space, Vec2d

from lib.camera import Camera
from lib.config import cfg
from lib.life import Life
from lib.math2 import clamp, flipy


class Meat(Life):

    def __init__(self, screen: Surface, space: Space, position: Vec2d, collision_tag: int, energy: int, color0: Color=Color('red'), color1: Color=Color('red4')):
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
        self.energy = int(energy/2)
        self.radius = self.eng_to_radius(self.energy)
        self._color0 = color0
        self._color1 = color1
        self.color0 = color0
        self.color1 = color1
        self.life_time = cfg.MEAT_TIME
        self.shape = Circle(self, self.radius)
        self.shape.collision_type = collision_tag
        space.add(self.shape)

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        x = self.position.x; y = flipy(self.position.y)
        r = self.radius / camera.scale
        rect = Rect(x-r, y-r, 2*r, 2*r)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        rx = rel_pos.x
        ry = rel_pos.y
        super().draw(screen, camera, selected)
        if r > 0:
            gfxdraw.filled_circle(screen, int(rx), int(ry), ceil(r), self.color1)
            if r > 2/camera.scale:
                gfxdraw.filled_circle(screen, int(rx), int(ry), ceil(r-2/camera.scale), self.color0)
        return True

    def update(self, dT: float, selected: Body):
        super().update(dT, selected)
        self.life_time -= dT
        if self.life_time <= 0:
            self.life_time = 0
        if self.energy <= 0:
            self.energy = 0
        alfa = int(200*(self.life_time/cfg.MEAT_TIME))+55
        alfa = clamp(alfa, 0, 255)
        #self._color0.a = alfa
        self.color0 = self._color0
        if self.energy > 0:
            new_size = self.eng_to_radius(self.energy)
            if new_size != self.shape.radius:
                self.shape.unsafe_set_radius(new_size)
                self.radius = new_size

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)

    def eng_to_radius(self, eng) -> int:
        return clamp(floor(log2(eng)/2), 1, 10)
