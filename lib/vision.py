from random import random, randint
from math import sin, cos, radians, degrees, pi as PI, floor, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect, draw
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.config import cfg
from lib.camera import Camera


class Vision(Circle):

    def __init__(self, body: Body, radius: int, wide: float, offset: float, description: str=""):
        super().__init__(body, radius)
        self.offset2 = offset
        self.wide = wide
        self.semiwide = wide/2
        self.collision_type = 4
        self.sensor = True
        self.base_color = Color(255, 255, 255, 75)
        self.seeing_color = Color(255, 0, 0, 200)
        self.active_color = self.base_color
        self.description = description
        self.max_dist = 0.0
        self.rng = pow(self.radius, 2)
        self.reset_detection()
        self.reset_range()

    def reset_detection(self):
        rng = self.rng
        self.detection = {
            'ang': 0.0,
            'dist': rng,
            'type': None,
            'target': None
        }

    def reset_range(self):
        rng = self.rng
        self.max_dist = rng

    def add_detection(self, angle: float, dist: float, target: Body, type: str, close_object: bool=False):
        if self.semiwide < abs(angle):
            if not close_object:
                return
            elif angle < 0:
                angle = -(self.semiwide)*0.9
            else:
                angle = (self.semiwide)*0.9
            
        if self.detection['dist'] > dist:
            self.detection = {
                'ang': angle,
                'dist': dist,
                'type': type,
                'target': target
            }
            self.max_dist = dist

    def get_detection(self) -> list:
        detection_l = -round((self.detection['ang']/(self.semiwide)), 1)
        detection_r = round((self.detection['ang']/(self.semiwide)), 1)
        detection_d = 1 - sqrt(self.detection['dist'])/cfg.SENSOR_RANGE
        type_enemy = 0
        type_plant = 0
        type_meat = 0
        detect_type = self.detection['type']
        if detect_type == 'creature':
            type_enemy = 1
        elif detect_type == 'plant':
            type_plant = 1
        elif detect_type == 'meat':
            type_meat = 1
        return [type_enemy, type_plant, type_meat, detection_d, detection_l, detection_r]
    
    def get_detection3(self) -> list:
        enemy_ang = round((self.enemy['ang']/(self.semiwide)), 1)
        enemy_d = 1 - sqrt(self.enemy['dist'])/cfg.SENSOR_RANGE
        plant_ang = round((self.plant['ang']/(self.semiwide)), 1)
        plant_d = 1 - sqrt(self.plant['dist'])/cfg.SENSOR_RANGE
        meat_ang = round((self.meat['ang']/(self.semiwide)), 1)
        meat_d = 1 - sqrt(self.meat['dist'])/cfg.SENSOR_RANGE
        return [enemy_ang, enemy_d, plant_ang, plant_d, meat_ang, meat_d]

    def set_detection_color(self, detection: bool):
        if detection:
            self.active_color = self.seeing_color
        else:
            self.active_color = self.base_color

    def draw(self, screen: Surface, camera: Camera, rel_position: Vector2, selected: bool=False):
        #if self.detection['target'] != None:
        #    self.set_detection_color(detection=True)
        r = int(self.radius)
        s = self.body.size
        v2 = (cos(self.body.angle+1)*(s*0.85), sin(self.body.angle+1)*(s*0.85))
        v3 = (cos(self.body.angle-1)*(s*0.85), sin(self.body.angle-1)*(s*0.85))
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        if selected:
            w1 = (int(cos(self.body.angle-self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle-self.semiwide)*(r+r*self.offset2[1])))
            w2 = (int(cos(self.body.angle+self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle+self.semiwide)*(r+r*self.offset2[1])))
            gfxdraw.arc(screen, x0, y0, r, int(degrees(self.body.angle-self.semiwide)), int(degrees(self.body.angle+self.semiwide)), self.active_color)
            gfxdraw.line(screen, x0, y0, x0+w1[0], y0+w1[1], self.active_color)
            gfxdraw.line(screen, x0, y0, x0+w2[0], y0+w2[1], self.active_color)
            detected = self.detection['type']
            if detected != None:
                color = Color(0, 0, 255, 150)
                if detected == 'plant':
                    color = Color(0, 255, 0, 150)
                elif detected == 'meat':
                    color = Color(255, 0, 0, 150)
                target = self.detection['target']
                rel_target_pos = camera.rel_pos(target.position)
                xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
                gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, color)
                gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, color)
        gfxdraw.aacircle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/10+1), Color('grey80'))
        gfxdraw.filled_circle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/10+1), Color('grey80'))
        gfxdraw.aacircle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/10+1), Color('grey80'))
        gfxdraw.filled_circle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/10+1), Color('grey80'))
        self.set_detection_color(detection=False)
        self.reset_detection()
        self.reset_range()