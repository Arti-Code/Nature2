from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect, draw
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.config import cfg

class SensorData():
    def __init__(self, max_angle: float, detection_range: float):
        self.max_angle = max_angle
        self.detection_range = cfg.SENSOR_RANGE
        self.enemy = False
        self.distance = -1
        self.direction = 0
        self.plant = False
        self.p_distance = -1
        self.p_direction = 0
        self.water = False
        self.water_distance = -1
        self.water_direction = 0
        self.meat = False
        self.meat_distance = -1
        self.meat_direction = 0
        self.detected = {
            'enemy': False, 'enemy_dist': -1, 
            'plant': False, 'plant_dist': -1, 
            'water': False, 'water_dist': -1, 
            'meat': False, 'meat_dist': -1,
            'rock': False, 'rock_dist': -1
        }

    def update(self, direction: float):
        self.direction = (direction/abs(self.max_angle))

    def send_data(self, detect: bool, distance: float, direction: float) -> float:
        self.enemy = detect
        if self.detection_range >= distance:
            self.detection_range = distance
            self.detected['enemy'] = detect
            if self.detection_range != 0:
                self.distance = 1 - (distance/cfg.SENSOR_RANGE)
                self.detected['enemy_dist'] = 1-(distance/cfg.SENSOR_RANGE)
            else:
                self.detected['enemy_dist'] = 0.1
                self.distance = 0.1
            self.direction = (direction/abs(self.max_angle))
        return self.detection_range

    def send_data2(self, detect: bool, distance: float, direction: float) -> float:
        self.plant = detect
        if self.detection_range >= distance:
            self.detection_range = distance
            self.detected['plant'] = detect
            if self.detection_range != 0:
                self.detected['plant_dist'] = 1-(distance/cfg.SENSOR_RANGE)
                self.p_distance = 1 - (distance/cfg.SENSOR_RANGE)
            else:
                self.detected['plant_dist'] = 0.1
                self.p_distance = 0.1
            self.p_direction = (direction/abs(self.max_angle))
        return self.detection_range

    def send_data3(self, detect: bool, distance: float, direction: float) -> float:
        self.water = detect
        if self.detection_range >= distance:
            #self.detection_range = distance
            self.detected['water'] = detect
            if self.detection_range != 0:
                self.detected['water_dist'] = 1-(distance/cfg.SENSOR_RANGE)
                self.water_distance = 1 - (distance/cfg.SENSOR_RANGE)
            else:
                self.detected['water_dist'] = 0.1
                self.water_distance = 0.1
            self.water_direction = (direction/abs(self.max_angle))
        return self.detection_range

    def send_data4(self, detect: bool, distance: float, direction: float) -> float:
        self.meat = detect
        if self.detection_range >= distance:
            self.detection_range = distance
            self.detected['meat'] = detect
            if self.detection_range != 0:
                self.detected['meat_dist'] = 1-(distance/cfg.SENSOR_RANGE)
                self.meat_distance = 1 - (distance/cfg.SENSOR_RANGE)
            else:
                self.detected['meat_dist'] = 0.1
                self.meat_distance = 0.1
            self.meat_direction = (direction/abs(self.max_angle))
        return self.detection_range

    def send_data5(self, detect: bool, distance: float, direction: float) -> float:
        self.meat = detect
        if self.detection_range >= distance:
            self.detection_range = distance
            self.detected['rock'] = detect
            if self.detection_range != 0:
                self.detected['rock_dist'] = 1-(distance/cfg.SENSOR_RANGE)
                self.meat_distance = 1 - (distance/cfg.SENSOR_RANGE)
            else:
                self.detected['rock_dist'] = 0.1
                self.meat_distance = 0.1
            self.meat_direction = (direction/abs(self.max_angle))
        return self.detection_range

    def reset(self):
        self.detection_range = cfg.SENSOR_RANGE
        self.enemy = False
        self.plant = False
        self.water = False
        self.meat = False
        self.distance = -1
        self.direction = 0
        self.p_distance = -1
        self.p_direction = 0
        self.water_distance = -1
        self.water_direction = 0
        self.meat_distance = -1
        self.meat_direction = 0
        self.detected = {
            'enemy': False, 'enemy_dist': -1, 
            'plant': False, 'plant_dist': -1, 
            'water': False, 'water_dist': -1, 
            'meat': False, 'meat_dist': -1,
            'rock': False, 'rock_dist': -1
        }

    def get_data(self) -> list:
        dist = max(self.detected['enemy_dist'], self.detected['plant_dist'], self.detected['water_dist'], self.detected['meat_dist'], self.detected['rock_dist'])
        return [self.detected['enemy_dist'], self.detected['plant_dist'], self.detected['water_dist'], self.detected['meat_dist'], self.detected['rock_dist']]
        
class Sensor():

    def __init__(self, screen: Surface, body: Body, collision_type: any, radians: float, length: int):
        self.body = body
        self.angle = radians
        self.length = length
        self.max_length = length
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.shape = Segment(body=body, a=(0,0), b=b, radius=1)
        self.shape.collision_type = collision_type
        self.shape.sensor = True
        self.data = SensorData(max_angle=cfg.SENSOR_MAX_ANGLE, detection_range=length)
        global white
        global red
        white = (255, 255, 255, 150)
        red = (255, 0, 0, 75)
        self.color = Color(white)
        self.water = False
        self.last_tile = None

    def update(self) -> tuple:
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.shape.unsafe_set_endpoints((0, 0), b)
        self.last_tile = Rect(x2-5, flipy(y2)-5, 10, 10)

    def draw(self, screen: Surface, rel_pos: Vector2):
        p1 = (rel_pos.x, rel_pos.y)
        rv = self.body.rotation_vector.rotated(self.angle)
        p2 = (p1[0]+rv[0]*self.length, p1[1]+rv[1]*self.length)
        #self.color.a = 75
        draw.aaline(screen, self.color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), 1)
        #if self.data.obstacle:
        #    c = (p1[0]+rv[0]*(1-self.data.obst_distance)*self.length, p1[1]+rv[1]*(1-self.data.obst_distance)*self.length)
        #    gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        if self.data.meat:
            c = (p1[0]+rv[0]*(1-self.data.water_distance)*self.length, p1[1]+rv[1]*(1-self.data.water_distance)*self.length)
            #gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        self.set_color(Color(white))

    def set_color(self, color: Color):
        self.color = color

    def rotate(self, delta_rad: float, min_angle: float, max_angle: float):
        angle = self.angle + delta_rad
        self.angle = clamp(angle, min_angle, max_angle)
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.update()

    def rotate_to(self, new_angle: float, min_angle: float, max_angle: float, dt: float):
        new_angle = clamp(new_angle, min_angle, max_angle)
        if new_angle != self.angle:
            delta_ang = cfg.SENSOR_SPEED * dt
            if new_angle < self.angle:
                self.angle -= delta_ang
            elif new_angle > self.angle:
                self.angle += delta_ang
            self.update()
            #self.angle = clamp(self.angle, min_angle, max_angle)
            #self.update()
            #x2, y2 = ang2vec2(self.angle)
            #b = (x2*self.length, y2*self.length)
            #self.shape.unsafe_set_endpoints((0, 0), b)

    def get_points(self) ->tuple:
        a = self.body.local_to_world((0, 0))
        b = self.body.local_to_world(self.shape.b)
        a = Vec2d(a[0], flipy(a[1]))
        b = Vec2d(b[0], flipy(b[1]))
        return (a, b)

    def send_data(self, detect: bool, distance: float):
        self.length = self.data.send_data(detect=detect, distance=distance, direction=self.angle)

    def send_data2(self, detect: bool, distance: float):
        self.length = self.data.send_data2(detect=detect, distance=distance, direction=self.angle)

    def send_data3(self, detect: bool, distance: float):
        self.length = self.data.send_data3(detect=detect, distance=distance, direction=self.angle)

    def send_data4(self, detect: bool, distance: float):
        self.length = self.data.send_data4(detect=detect, distance=distance, direction=self.angle)

    def send_data5(self, detect: bool, distance: float):
        self.length = self.data.send_data5(detect=detect, distance=distance, direction=self.angle)

    def reset_data(self):
        self.data.reset()
        self.length = self.max_length

    def get_input(self) -> dict:
        return self.data.get_data()