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
        self.max_dist_enemy = 0.0
        self.max_dist_plant = 0.0
        self.max_dist_meat = 0.0
        self.rng = pow(self.radius, 2)
        self.reset_detection()
        self.reset_range()

    def reset_detection(self):
        rng = self.rng
        self.enemy = {
            'ang': 0.0,
            'dist': rng,
            'target': None
        }
        self.plant = {
            'ang': 0.0,
            'dist': rng,
            'target': None
        }
        self.meat = {
            'ang': 0.0,
            'dist': rng,
            'target': None
        }
        #self.reset_range()

    def reset_range(self):
        rng = self.rng
        self.max_dist_enemy = rng
        self.max_dist_plant = rng
        self.max_dist_meat = rng

    def add_detection(self, angle: float, dist: float, target: Body, type: str, close_object: bool=False):
        if self.semiwide < abs(angle):
            if not close_object:
                return
            elif angle < 0:
                angle = -(self.semiwide)*0.9
                #angle = (self.semiwide) * (angle/abs(angle))
            else:
                angle = (self.semiwide)*0.9
        dist2 = dist*1.1
        if type == 'creature':
            #dist1 = self.enemy['dist']*(abs(self.enemy['ang'])/(self.semiwide))
            dist1 = self.enemy['dist']
            if dist1 > dist2:
                self.enemy = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_enemy = dist
        elif type == 'plant':
            #dist1 = self.plant['dist']*(abs(self.plant['ang'])/(self.semiwide))
            dist1 = self.plant['dist']
            if dist1 > dist2:
                self.plant = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_plant = dist
        elif type == 'meat':
            #dist1 = self.meat['dist']*(abs(self.meat['ang'])/(self.semiwide))
            dist1 = self.meat['dist']
            if dist1 > dist2:
                self.meat = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_meat = dist

    def update_max_dist(self):
        self.max_dist = max([self.enemy['dist'], self.plant['dist'], self.meat['dist']])

    def get_detection(self) -> list:
        enemy_l = round((self.enemy['ang']/(self.semiwide)), 1)
        enemy_r = round((self.enemy['ang']/(self.semiwide)), 1)
        if enemy_r < 0:
            enemy_r = 0
        else:
            #enemy_r = enemy_r
            pass
        if enemy_l >= 0:
            enemy_l = 0
        else:
            enemy_l = -enemy_l
        enemy_d = 1 - sqrt(self.enemy['dist'])/cfg.SENSOR_RANGE
        plant_l = round((self.plant['ang']/(self.semiwide)), 1)
        plant_r = round((self.plant['ang']/(self.semiwide)), 1)
        if plant_r < 0:
            plant_r = 0
        else:
            #plant_r = plant_r
            pass
        if plant_l >= 0:
            plant_l = 0
        else:
            plant_l = -plant_l
        plant_d = 1 - sqrt(self.plant['dist'])/cfg.SENSOR_RANGE
        meat_l = round((self.meat['ang']/(self.semiwide)), 1)
        meat_r = round((self.meat['ang']/(self.semiwide)), 1)
        if meat_r < 0:
            meat_r = 0
        else:
            #meat_r = meat_r
           pass
        if meat_l >= 0:
            meat_l = 0
        else:
            meat_l = -meat_l
        meat_d = 1 - sqrt(self.meat['dist'])/cfg.SENSOR_RANGE
        return [enemy_l, enemy_r, enemy_d, plant_l, plant_r, plant_d, meat_l, meat_r, meat_d]
    
    def set_detection_color(self, detection: bool):
        if detection:
            self.active_color = self.seeing_color
        else:
            self.active_color = self.base_color

    def draw(self, screen: Surface, camera: Camera, rel_position: Vector2):
        #if self.detection['target'] != None:
        #    self.set_detection_color(detection=True)
        r = int(self.radius)
        w1 = (int(cos(self.body.angle-self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle-self.semiwide)*(r+r*self.offset2[1])))
        w2 = (int(cos(self.body.angle+self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle+self.semiwide)*(r+r*self.offset2[1])))
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        v = self.body.rotation_vector * r
        x = x0 + v.x; y = y0 + v.y
        s = self.body.size
        v2 = (cos(self.body.angle+1)*s, sin(self.body.angle+1)*s)
        v3 = (cos(self.body.angle-1)*s, sin(self.body.angle-1)*s)
        gfxdraw.arc(screen, x0, y0, r, int(degrees(self.body.angle-self.semiwide)), int(degrees(self.body.angle+self.semiwide)), self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w1[0], y0+w1[1], self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w2[0], y0+w2[1], self.active_color)
        gfxdraw.aacircle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.aacircle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        if self.enemy['target'] != None:
            target = self.enemy['target']
            rel_target_pos = camera.rel_pos(target.position)
            xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
            gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(255, 0, 0, 150))
            gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(255, 0, 0, 150))
        if self.plant['target'] != None:
            target = self.plant['target']
            rel_target_pos = camera.rel_pos(target.position)
            xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
            gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(0, 255, 0, 150))
            gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(0, 255, 0, 150))
        if self.meat['target'] != None:
            target = self.meat['target']
            rel_target_pos = camera.rel_pos(target.position)
            xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
            gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(0, 0, 255, 150))
            gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(0, 0, 255, 150))
        self.set_detection_color(detection=False)
        self.reset_detection()
        self.reset_range()