from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space
from lib.math2 import flipy, ang2vec, ang2vec2

class Detector():

    def __init__(self, screen: Surface, body: Body, collision_type: any, degree_angle: int, length: int):
        self.screen = screen
        self.body = body
        self.angle = degree_angle
        self.length = length
        x2, y2 = ang2vec2(radians(degree_angle))
        b = (x2*length, y2*length)
        self.shape = Segment(body=body, a=(0,0), b=b, radius=1)
        self.shape.collision_type = collision_type
        self.shape.sensor = True
        self.color = Color('white')

    def draw(self):
        p1 = (self.shape.body.position.x, self.shape.body.position.y)
        rv = (self.body.rotation_vector.rotated_degrees(self.angle))*self.length
        p2 = (p1[0]+rv[0], p1[1]+rv[1])
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]), flipy(int(p2[1])), self.color)

    def set_color(self, color: Color):
        self.color = color

class Life(Body):

    def __init__(self, screen: Surface, space: Space, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, angle: float=None, visual_range: int=100, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.detectors = []
        self.eye_colors = {}
        self.visual_range = visual_range
        #self.body = Body(body_type=Body.KINEMATIC)
        if position is not None:
            self.body.position = position
        else:
            x = randint(50, world_size[0]-50)
            y = randint(50, world_size[1]-50)
            self.position = (x, y)
        self.angle = random()*2*PI
        space.add(self)
        self.shape = Circle(body=self, radius=size, offset=(0, 0))
        self.shape.collision_type = 2
        space.add(self.shape)
        self.detectors = []
        self.detectors.append(Detector(screen, self, 4, 0, 150))
        space.add(self.detectors[0].shape)
        self.detectors.append(Detector(screen, self, 4, 45, 150))
        space.add(self.detectors[1].shape)
        self.detectors.append(Detector(screen, self, 4, -45, 150))
        space.add(self.detectors[2].shape)

    def draw(self):
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        rot = self.rotation_vector
        self.draw_detectors()
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r), self.color0)
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r-2), self.color1)
        if r > 2:
            x2 = round(x + rot.x*r)
            y2 = round(y + rot.y*r)
            r2 = round(r/2)
            gfxdraw.filled_circle(self.screen, x2, flipy(y2), r2, self.color2)

    def draw_detectors(self):
        for detector in self.detectors:
            detector.draw()

    def update(self, space: Space, dt:float, detections: list=[]) -> None:
        self.update_detections(detections)
        self.random_move(space, dt)

    def update_detections(self, detections: list):        
        for detector in self.detectors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def random_move(self, space: Space, dt: float) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.05
        move = random()*speed
        turn = random()*2-1
        self.angle = (self.angle+(turn*rot_speed))%(2*PI)
        self.vdir = self.rotation_vector
        self.velocity = move*self.vdir/dt
       
