from math import ceil
from math import pi as PI
from math import sin
from random import randint

import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface
from pygame.math import Vector2
from pymunk import Body, Space, Vec2d

from lib.camera import Camera
from lib.config import cfg
from lib.math2 import flipy


class Life(Body):

    def __init__(self, screen: Surface, space: Space, collision_tag: int, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        if position is not None:
            self.position = position
        else:
            x = randint(50, cfg.WORLD[0]-50)
            y = randint(50, cfg.WORLD[1]-50)
            self.position = Vec2d(x, y)
        space.add(self)
        self.selection_time = 0
        self.water_ahead = False
        self.border: bool = False
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False
        self.collide_meat = False
        self.rect = Rect(self.position.x-5, flipy(self.position.y)-5, 10, 10)

    def draw(self, screen: Surface, camera: Camera, selected: Body):
        if self == selected:
            rel_pos = camera.rel_pos(Vector2(self.position.x, flipy(self.position.y)))
            x =rel_pos.x; y =rel_pos.y
            r = ceil(self.shape.radius / camera.scale)
            self.draw_selection(screen, x, y, r)

    def update(self, dt: float, selected: Body):
        r = self.shape.radius
        self.rect = Rect(self.position.x-r, flipy(self.position.y)-r, 2*r, 2*r)
        if self == selected:
            self.selection_time += dt*2
            self.selection_time = self.selection_time%(PI)
        else:
            self.selection_time = 0
        self.check_edges()

    def check_edges(self):
        y = self.position.y; x = self.position.x;
        if self.position.x <= 0:
            x = 2
            self.position = Vec2d(x, y)
            self.border = True
        elif self.position.x >= cfg.WORLD[0]:
            x = cfg.WORLD[0]-2
            self.position = Vec2d(x, y)
            self.border = True
        if self.position.y <= 0:
            y = 2
            self.position = Vec2d(x, y)
            self.border = True
        elif self.position.y >= cfg.WORLD[1]:
            y = cfg.WORLD[1]-2
            self.position = Vec2d(x, y)
            self.border = True

    def get_tile_coord(self) -> tuple:
        x = self.position.x; y = flipy(self.position.y)
        return (int(x/cfg.TILE_RES), int(y/cfg.TILE_RES))
    
    def draw_selection(self, screen: Surface, x, y, r):
        color = Color('orange')
        c = abs(sin(self.selection_time))
        gfxdraw.aacircle(screen, int(x), int(y), int(r+3+(r+2)*c), color)
        gfxdraw.aacircle(screen, int(x), int(y), int(r+3+(r+3)*c), color)

    


