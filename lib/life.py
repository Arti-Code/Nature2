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
        self.world_size = world_size
        self.max_energy = 200
        self.energy = 200
        self.output = []
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.neuro = Network()
        self.neuro.BuildRandom([12, 0, 0, 0, 3], 0.2)
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
        self.draw_energy_bar(int(x), flipy(int(y)))
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
        self.analize()
        move_energy = self.random_move(space, dt)
        base_energy = 1/dt
        self.energy -= (move_energy + base_energy)

    def update_detections(self, detections: list):        
        for detector in self.sensors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def random_move(self, space: Space, dt: float) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.1
        move = self.output[0]
        turn = self.output[1]
        sensor_turn = self.output[2]/dt*rot_speed
        #self.angle = (self.angle+(turn*rot_speed)/dt)%(2*PI)
        self.vdir = self.rotation_vector
        self.velocity = move*self.vdir/dt
        self.sensors[1].rotate(sensor_turn, 0, PI/1.5)
        self.sensors[2].rotate(-sensor_turn, -PI/1.5, 0)
        return move/dt

    def get_input(self):
        input = []
        x = self.position[0]/self.world_size[0]
        input.append(x)
        y = self.position[1]/self.world_size[1]
        input.append(y)
        eng = self.energy/self.max_energy
        input.append(eng)
        for sensor in self.sensors:
            e, d, a = sensor.get_input()
            d = round(d, 3)
            a = round(a%PI, 3)
            input.append(e)
            input.append(d)
            input.append(a)
        return input

    def analize(self):
        input = self.get_input()
        self.output = self.neuro.Calc(input)
        for sensor in self.sensors:
            sensor.reset_data()
            
       
    def draw_energy_bar(self, rx: int, ry: int):
        bar_red = Color(255, 0, 0)
        bar_green = Color(0, 255, 0)
        size = self.shape.radius
        gfxdraw.box(self.screen, Rect(rx-round(10), ry+round(size+3), round(19), 1), bar_red)
        gfxdraw.box(self.screen, Rect(rx-round(10), ry+round(size+3), round(20*(self.energy/self.max_energy)), 1), bar_green)
