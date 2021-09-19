from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp

class SensorData():
    def __init__(self, max_angle: float, detection_range: float):
        self.max_angle = max_angle
        self.detection_range = detection_range
        self.enemy = False
        self.distance = -1
        self.direction = 0
        self.plant = False
        self.p_distance = -1
        self.p_direction = 0
        self.obstacle = False
        self.obst_distance = -1
        self.obst_direction = 0
        self.meat = False
        self.meat_distance = -1
        self.meat_direction = 0

    def update(self, direction: float):
        self.direction = (direction/abs(self.max_angle))

    def send_data(self, detect: bool, distance: float, direction: float):
        self.enemy = detect
        self.distance = 1 - (distance/self.detection_range)
        self.direction = (direction/abs(self.max_angle))

    def send_data2(self, detect: bool, distance: float, direction: float):
        self.plant = detect
        self.p_distance = 1 - (distance/self.detection_range)
        self.p_direction = (direction/abs(self.max_angle))

    def send_data3(self, detect: bool, distance: float, direction: float):
        self.obstacle = detect
        self.obst_distance = 1 - (distance/self.detection_range)
        self.obst_direction = (direction/abs(self.max_angle))

    def send_data4(self, detect: bool, distance: float, direction: float):
        self.meat = detect
        self.meat_distance = 1 - (distance/self.detection_range)
        self.meat_direction = (direction/abs(self.max_angle))

    def reset(self):
        self.enemy = False
        self.plant = False
        self.obstacle = False
        self.meat = False
        self.distance = -1
        self.direction = 0
        self.p_distance = -1
        self.p_direction = 0
        self.obst_distance = -1
        self.obst_direction = 0
        self.meat_distance = -1
        self.meat_direction = 0

    def get_data(self):
        return (self.enemy, self.distance, self.direction, self.plant, self.p_distance, self.p_direction, self.obstacle, self.obst_distance, self.obst_direction, self.meat, self.meat_distance, self.meat_direction)
        
class Sensor():

    def __init__(self, screen: Surface, body: Body, collision_type: any, radians: float, length: int):
        #self.screen = screen
        self.body = body
        self.angle = radians
        self.length = length
        x2, y2 = ang2vec2(radians)
        b = (x2*length, y2*length)
        self.shape = Segment(body=body, a=(0,0), b=b, radius=1)
        self.shape.collision_type = collision_type
        self.shape.sensor = True
        self.data = SensorData(max_angle=PI, detection_range=length)
        global white
        global red
        white = (255, 255, 255, 150)
        red = (255, 0, 0, 75)
        self.color = Color(white)

    def draw(self, screen: Surface, rel_pos: Vector2):
        p1 = (rel_pos.x, rel_pos.y)
        rv = self.body.rotation_vector.rotated(self.angle)
        p2 = (p1[0]+rv[0]*self.length, p1[1]-rv[1]*self.length)
        self.color.a = 25
        gfxdraw.line(screen, int(p1[0]), (int(p1[1])), int(p2[0]), (int(p2[1])), self.color)
        #if self.data.obstacle:
        #    c = (p1[0]+rv[0]*(1-self.data.obst_distance)*self.length, p1[1]+rv[1]*(1-self.data.obst_distance)*self.length)
        #    gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        if self.data.meat:
            c = (p1[0]+rv[0]*(1-self.data.obst_distance)*self.length, p1[1]+rv[1]*(1-self.data.obst_distance)*self.length)
            #gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        self.set_color(Color(white))

    def set_color(self, color: Color):
        self.color = color

    def rotate(self, delta_rad: float, min_angle: float, max_angle: float):
        angle = self.angle + delta_rad
        self.angle = clamp(angle, min_angle, max_angle)
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.shape.unsafe_set_endpoints((0, 0), b)

    def send_data(self, detect: bool, distance: float):
        self.data.send_data(detect=detect, distance=distance, direction=self.angle)

    def send_data2(self, detect: bool, distance: float):
        self.data.send_data2(detect=detect, distance=distance, direction=self.angle)

    def send_data3(self, detect: bool, distance: float):
        self.data.send_data3(detect=detect, distance=distance, direction=self.angle)

    def send_data4(self, detect: bool, distance: float):
        self.data.send_data4(detect=detect, distance=distance, direction=self.angle)

    def reset_data(self):
        self.data.reset()

    def get_input(self):
        return self.data.get_data()

class PolySensor():

    def __init__(self, screen: Surface, body: Body, collision_type: any, angle: int, radial_width: int, length: int, min_angle: int, max_angle: int):
        self.screen = screen
        self.body = body
        self.angle = angle
        self.length = length
        self.radial_width = radial_width
        self.min_angle = min_angle
        self.max_angle = max_angle
        x1, y1 = ang2vec2(radians((angle+radial_width/2)%360))
        x2, y2 = ang2vec2(radians((angle-radial_width/2)%360))
        v1 = (x1*length, y1*length)
        v2 = (x2*length, y2*length)
        v0 = (0, 0)
        self.verts = [v0, v1, v2]
        self.shape = Poly(body=body, vertices=self.verts)
        self.shape.collision_type = collision_type
        self.shape.sensor = True
        self.color = Color('white')

    def draw(self):
        p0 = (self.shape.body.position.x, self.shape.body.position.y)
        rv1 = self.body.rotation_vector.rotated_degrees((self.angle+self.radial_width/2)%360)*self.length
        rv2 = self.body.rotation_vector.rotated_degrees((self.angle-self.radial_width/2)%360)*self.length
        p1 = (p0[0]+rv1[0], p0[1]+rv1[1])
        p2 = (p0[0]+rv2[0], p0[1]+rv2[1])
        color = self.color
        color.a = 125
        gfxdraw.line(self.screen, int(p0[0]), flipy(int(p0[1])), int(p1[0]), flipy(int(p1[1])), color)
        gfxdraw.line(self.screen, int(p0[0]), flipy(int(p0[1])), int(p2[0]), flipy(int(p2[1])), color)
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]), flipy(int(p2[1])), color)

    def set_color(self, color: Color):
        self.color = color

    def change_angle(self, delta_angle: float):
        transform = Transform.rotation(radians(delta_angle))
        self.shape.unsafe_set_vertices(self.verts, transform)
        print('.')

    def rotate(self, degrees: float):
        mini = min(0, self.angle)
        maxi = max(0, self.angle)
        angle = self.angle + degrees
        if angle > self.min_angle and angle < self.max_angle:
            self.angle = angle
            x1, y1 = ang2vec2(radians((self.angle+self.radial_width/2)%360))
            x2, y2 = ang2vec2(radians((self.angle-self.radial_width/2)%360))
            v1 = (x1*self.length, y1*self.length)
            v2 = (x2*self.length, y2*self.length)
            v0 = (0, 0)
            self.verts = [v0, v1, v2]
            self.shape.unsafe_set_vertices(self.verts)
