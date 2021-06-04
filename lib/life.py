from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor, PolySensor
from lib.net import Network


class Life(Body):

    def __init__(self, screen: Surface, space: Space, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, angle: float=None, visual_range: int=180, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.neuro = Network()
        self.neuro.BuildRandom([3, 0, 0, 0, 3], 0.2)
        self.sensors = []
        self.eye_colors = {}
        self.visual_range = visual_range
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
        self.sensors = []
        self.sensors.append(Sensor(screen, self, 4, 0, 220))
        space.add(self.sensors[0].shape)
        self.sensors.append(Sensor(screen, self, 4, PI/3, 220))
        space.add(self.sensors[1].shape)
        self.sensors.append(Sensor(screen, self, 4, -PI/3, 220))
        space.add(self.sensors[2].shape)

    def draw(self):
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        rot = self.rotation_vector
        #self.draw_detectors()
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r), self.color0)
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r-2), self.color1)
        if r > 2:
            x2 = round(x + rot.x*r)
            y2 = round(y + rot.y*r)
            r2 = round(r/2)
            gfxdraw.filled_circle(self.screen, x2, flipy(y2), r2, self.color2)
        self.color0 = Color('green')

    def draw_detectors(self):
        for detector in self.sensors:
            detector.draw()

    def update(self, space: Space, dt:float, detections: list=[]) -> None:
        #self.update_detections(detections)
        self.random_move(space, dt)

    def update_detections(self, detections: list):        
        for detector in self.sensors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def random_move(self, space: Space, dt: float) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.02
        move = random()*speed
        turn = random()*2-1
        senor_turn = (random()*2-1)/dt
        self.angle = (self.angle+(turn*rot_speed))%(2*PI)
        self.vdir = self.rotation_vector
        self.velocity = move*self.vdir/dt
        self.sensors[1].rotate(senor_turn, 0, PI/1.5)
        self.sensors[2].rotate(-senor_turn, -PI/1.5, 0)
       
