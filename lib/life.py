from typing import overload
from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle
from lib.math2 import flipy

class Life():

    def __init__(self, screen: Surface, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, angle: float=None, position: Vec2d=None):
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.angle: float = 0.0
        self.vdir: Vec2d
        if angle is None:
            self.angle = random()*2*PI
        else:
            self.angle = angle%(2*PI)
        mass = size
        inertia = pm.moment_for_circle(mass=mass, inner_radius=0, outer_radius=size, offset=(0,0))
        self.body = Body(mass=mass, moment=inertia, body_type=Body.KINEMATIC)
        if position is not None:
            self.body.position = position
        else:
            x = randint(0, world_size.x)
            y = randint(0, world_size.y)
            self.body.position = x, y
        self.shape = Circle(body=self.body, radius=size, offset=(0, 0))
        self.shape.collision_type = 1

    def get_body_and_shape(self) -> tuple:
        return (self.body, self.shape)

    def get_pos(self) -> Vec2d:
        return Vec2d(self.body.position.x, self.body.position.y)

    def get_pos_xy(self) -> tuple:
        return (int(self.body.position.x), int(self.body.position.y))

    def set_pos(self, pos: Vec2d) -> None:
        self.body.position = pos

    def mod_pos(self, delta_pos: Vec2d) -> None:
        self.body.position += delta_pos

    @overload
    def set_pos(self, x: float, y:float) -> None:
        self.body.position = Vec2d(x, y)

    def get_size(self) -> float:
            return self.shape.radius

    def ang_to_vec2d(self, angle: float) -> Vec2d:
        x: float = sin(angle)
        y: float = cos(angle)
        return Vec2d(x, y)

    def ang_to_xy(self, angle: float) -> tuple:
        x: float = sin(angle)
        y: float = cos(angle)
        return (x, y)

    def draw(self):
        # * -=VARs=-
        x: int; y: int; x2: int; y2: int; r: int; r2: int; v: Vec2d 
        x, y = self.get_pos_xy()
        r = int(self.get_size())
        v = self.vdir
        # * -=MAIN BODY PART=- *
        gfxdraw.filled_circle(self.screen, x, flipy(y), r, self.color0)
        gfxdraw.filled_circle(self.screen, x, flipy(y), r-2, self.color1)
        # * -=FRONT BODY (HEAD)=- *
        if r > 2:
            x2 = round(x + v.x*r)
            y2 = round(y + v.y*r)
            r2 = round(r/2)
            gfxdraw.filled_circle(self.screen, x2, flipy(y2), round(r/2), self.color2)

    def update(self, dT:float) -> None:
        self.random_move()
        #points_set = self.shape.shapes_collide()
        #if points_set != None:
        #    print('collision')

    def random_move(self) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.1
        move = random()*speed
        turn = randint(-1, 1)
        self.angle = (self.angle+(turn*rot_speed))%(2*PI)
        self.vdir = self.ang_to_vec2d(self.angle)
        delta_pos = self.vdir*move
        self.mod_pos(delta_pos=delta_pos)

