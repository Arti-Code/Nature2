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
        self.obstacle = False
        self.obst_distance = -1
        self.obst_direction = 0
        self.meat = False
        self.meat_distance = -1
        self.meat_direction = 0
        self.detected = {
            'enemy': False, 'enemy_dist': -1, 
            'plant': False, 'plant_dist': -1, 
            'obstacle': False, 'obstacle_dist': -1, 
            'meat': False, 'meat_dist': -1
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
        self.obstacle = detect
        if self.detection_range >= distance:
            self.detection_range = distance
            self.detected['obstacle'] = detect
            if self.detection_range != 0:
                self.detected['obstacle_dist'] = 1-(distance/cfg.SENSOR_RANGE)
                self.obst_distance = 1 - (distance/cfg.SENSOR_RANGE)
            else:
                self.detected['obstacle_dist'] = 0.1
                self.obst_distance = 0.1
            self.obst_direction = (direction/abs(self.max_angle))
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

    def reset(self):
        self.detection_range = cfg.SENSOR_RANGE
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
        self.detected = {
            'enemy': False, 'enemy_dist': -1, 
            'plant': False, 'plant_dist': -1, 
            'obstacle': False, 'obstacle_dist': -1, 
            'meat': False, 'meat_dist': -1
        }

    def get_data(self) -> list:
        dist = max(self.detected['enemy_dist'], self.detected['plant_dist'], self.detected['obstacle_dist'], self.detected['meat_dist'])
        #return self.detected
        return [self.detected['enemy'], self.detected['plant'], self.detected['obstacle'], self.detected['meat'], dist]
        
class Sensor():

    def __init__(self, screen: Surface, body: Body, collision_type: any, radians: float, length: int):
        #self.screen = screen
        self.body = body
        self.angle = radians
        self.length = length
        self.max_length = length
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.shape = Segment(body=body, a=(0,0), b=b, radius=1)
        #l = min([self.body.x, self.body.x+b[0]])
        #r = max([self.body.x, self.body.x+b[0]])
        #t = min([flipy(self.body.y), flipy(self.body.y)+b[1]])
        #d = max([flipy(self.body.y), flipy(self.body.y)+b[1]])
        #self.rect = Rect(l, t, r-l, d-t)
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
        #x2, y2 = ang2vec2(self.angle+self.body.angle)
        x2, y2 = ang2vec2(self.angle)
        b = (x2*self.length, y2*self.length)
        self.shape.unsafe_set_endpoints((0, 0), b)
        self.last_tile = Rect(x2-5, flipy(y2)-5, 10, 10)

    def draw(self, screen: Surface, rel_pos: Vector2):
        p1 = (rel_pos.x, rel_pos.y)
        rv = self.body.rotation_vector.rotated(self.angle)
        p2 = (p1[0]+rv[0]*self.length, p1[1]-rv[1]*self.length)
        #self.color.a = 75
        draw.aaline(screen, self.color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), 1)
        #if self.data.obstacle:
        #    c = (p1[0]+rv[0]*(1-self.data.obst_distance)*self.length, p1[1]+rv[1]*(1-self.data.obst_distance)*self.length)
        #    gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        if self.data.meat:
            c = (p1[0]+rv[0]*(1-self.data.obst_distance)*self.length, p1[1]+rv[1]*(1-self.data.obst_distance)*self.length)
            #gfxdraw.filled_circle(screen, int(c[0]), flipy(int(c[1])), 1, Color('yellow'))
        self.set_color(Color(white))
        #rect = self.get_rect()
        self.get_water_detectors(screen)


    def get_water_detectors(self, screen: Surface) -> list:
        x = self.body.position.x; y = flipy(self.body.position.y)
        p1 = (x, y)
        rv = self.body.rotation_vector.rotated(self.angle)
        tiles = []
        for n in range(1,5):
            l = round((p1[0]+rv[0]*40*n)/10)
            t = round((p1[1]-rv[1]*40*n)/10)
            tile = Rect(l*10-5, t*10-5, 10, 10)
            draw.rect(screen, Color((255, 125, 0)), tile, 1)
            tiles.append((l, t))
        return tiles

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

    def get_rect(self) -> Rect:
        l = int(self.shape.bb[0])
        b = int(self.shape.bb[3])
        r = int(self.shape.bb[2])
        t = int(self.shape.bb[1])
        return Rect(l, b, r-l, t-b)

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

    def detect_water(self, detect: bool):
        self.water = detect

    def reset_data(self):
        self.data.reset()
        self.length = self.max_length
        #self.water = False

    def get_input(self) -> dict:
        return self.data.get_data()