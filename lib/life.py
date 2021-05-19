from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment
from lib.math2 import flipy


class Life():

    def __init__(self, screen: Surface, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, angle: float=None, visual_range: int=150, position: Vec2d=None):
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.eye_color = Color('white')
        self.visual_range = visual_range
        self.vdir: Vec2d
        mass = size
        inertia = pm.moment_for_circle(mass=mass, inner_radius=0, outer_radius=size, offset=(0,0))
        self.body = Body(mass=mass, moment=inertia, body_type=Body.KINEMATIC)
        #if angle is None:
        #    self.body.angle = random()*2*PI
        #else:
        #    self.body.angle = angle%(2*PI)
        self.body.angle = 0.5*PI
        if position is not None:
            self.body.position = position
        else:
            x = randint(50, world_size.x-50)
            y = randint(50, world_size.y-50)
            self.body.position = (x, y)
        self.shape = Circle(body=self.body, radius=size, offset=(0, 0))
        self.shape.body = self.body
        self.shape.collision_type = 2
        p1 = Vec2d(0, 0)
        p2 = Vec2d(sin(self.body.angle), cos(self.body.angle))
        p2 = p2.normalized()
        self.eye = Segment(self.body, p1, p2*self.visual_range, 1)
        #self.eye = Segment(self.body, self.body.position, self.body.position+self.ang_to_vec2d(self.body.angle)*self.visual_range, 1)
        self.eye.collision_type = 4
        self.eye.sensor = True
        self.eye.body = self.body
        #self.shape.friction = 0.9

    def get_body_and_shapes(self) -> tuple:
        return (self.body, self.shape, self.eye)

    def get_pos(self) -> Vec2d:
        return Vec2d(self.body.position.x, self.body.position.y)

    def get_pos_xy(self) -> tuple:
        return (self.body.position.x, self.body.position.y)

    def set_pos(self, pos: Vec2d) -> None:
        self.body.position = pos

    def mod_pos(self, delta_pos: Vec2d) -> None:
        self.body.position += delta_pos

    def set_pos_xy(self, x: float, y:float) -> None:
        self.body.position = Vec2d(x, y)

    def get_size(self) -> float:
        return self.shape.radius

    def ang_to_vec2d(self, angle: float) -> Vec2d:
        y: float = sin(angle)
        x: float = cos(angle)
        return Vec2d(x, y)

    def ang_to_xy(self, angle: float) -> tuple:
        x: float = sin(angle)
        y: float = cos(angle)
        return (x, y)

    def set_velocity(self, v: Vec2d):
        self.shape.body.velocity = v

    def draw(self):
        # * -=VARs=-
        x2: int; y2: int; x3: int; y3: int; r: int; r2: int; v: Vec2d 
        x, y = self.get_pos_xy()
        r = int(self.get_size())
        v = self.ang_to_vec2d(self.body.angle)
        v = v.normalized()
        x3 = v.x; y3 = v.y
        gfxdraw.line(self.screen, int(x), flipy(int(y)), int(x+x3*self.visual_range), flipy(int(y+y3*self.visual_range)), self.eye_color)
        #gfxdraw.line(self.screen, int(self.eye.a.x), int(flipy(self.eye.a.y)), int(self.eye.b.x), flipy(int(self.eye.b.y)), Color('#40e0d0'))
        # * -=MAIN BODY PART=- *
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), r, self.color0)
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), r-2, self.color1)
        # * -=FRONT BODY (HEAD)=- *
        if r > 2:
            x2 = round(x + v.x*r)
            y2 = round(y + v.y*r)
            r2 = round(r/2)
            gfxdraw.filled_circle(self.screen, x2, flipy(y2), r2, self.color2)

    def update(self, dt:float, eyes: list=[]) -> None:
        self.eye_color = Color('white')
        if self.eye in eyes:
            self.eye_color = Color('red')
        self.random_move(dt)

    def random_move(self, dt: float) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.1
        move = random()*speed
        turn = randint(-1, 1)
        self.body.angle = (self.body.angle+(turn*rot_speed))%(2*PI)
        self.vdir = self.ang_to_vec2d(self.body.angle)
        self.set_velocity(move*self.vdir/dt)
        #self.eye.position = self.body.position
        #self.eye.b = self.body.position+self.vdir*self.visual_range

    #def update_vision(self):
    #    self.eye.a = self.body.position
    #    self.eye.b = self.vdir * self.visual_range

