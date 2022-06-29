from random import random, randint
from math import sin, cos, radians, degrees, pi as PI, floor, sqrt
from enum import Enum
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect, draw
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.config import cfg
from lib.camera import Camera

class TARGET_TYPE(Enum):
    ENEMY   = 0
    PLANT   = 1
    MEAT    = 2
    ROCK    = 3

class Target():

    def __init__(self, type: TARGET_TYPE, position: Vec2d, sqrt_distance: float=0.0, angle: float=0.0):
        self.type: TARGET_TYPE=type
        self.position = position
        self.sqrt_distance = sqrt_distance
        self.angle = angle

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
        self.max_dist_rock = 0.0
        self.max_dist = 0.0
        self.rng = pow(self.radius, 2)
        self.reset_detection()
        self.reset_range()
        self.observe: bool=True
        self.observe_done: int=-1

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
        self.rock = {
            'ang': 0.0,
            'dist': rng,
            'target': None
        }
        self.observe_done = -1
        #self.update_max_dist()

    def allow_observe(self, allow: bool):
        self.observe = allow

    def reset_range(self):
        rng = self.rng
        self.max_dist_enemy = rng
        self.max_dist_plant = rng
        self.max_dist_meat = rng
        self.max_dist_rock = rng
        self.max_dist = rng

    def add_detection(self, angle: float, dist: float, target: Body, type: str, close_object: bool=False):
        if self.semiwide < abs(angle):
            if not close_object:
                return
            elif angle < 0:
                angle = -(self.semiwide)*0.9
            else:
                angle = (self.semiwide)*0.9

        if type == 'creature':
            if self.enemy['dist'] > dist:
                self.enemy = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_enemy = dist
                if self.max_dist > dist:
                    self.max_dist = dist
        elif type == 'plant':
            dist1 = self.plant['dist']
            if self.plant['dist'] > dist:
                self.plant = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_plant = dist
                if self.max_dist > dist:
                    self.max_dist = dist
        elif type == 'meat':
            dist1 = self.meat['dist']
            if self.meat['dist'] > dist:
                self.meat = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_meat = dist
                if self.max_dist > dist:
                    self.max_dist = dist
        elif type == 'rock':
            dist1 = self.rock['dist']
            if self.rock['dist'] > dist:
                self.rock = {
                    'ang': angle,
                    'dist': dist,
                    'target': target
                }
                self.max_dist_rock = dist
                if self.max_dist > dist:
                    self.max_dist = dist

    def update_max_dist(self):
        self.max_dist = min([self.enemy['dist'], self.plant['dist'], self.meat['dist'], self.rock['dist']])

    def get_detection(self) -> list:
        enemy_l = -round((self.enemy['ang']/(self.semiwide)), 1)
        enemy_r = round((self.enemy['ang']/(self.semiwide)), 1)
        enemy_d = 1 - sqrt(self.enemy['dist'])/cfg.SENSOR_RANGE
        plant_l = -round((self.plant['ang']/(self.semiwide)), 1)
        plant_r = round((self.plant['ang']/(self.semiwide)), 1)
        plant_d = 1 - sqrt(self.plant['dist'])/cfg.SENSOR_RANGE
        meat_l = -round((self.meat['ang']/(self.semiwide)), 1)
        meat_r = round((self.meat['ang']/(self.semiwide)), 1)
        meat_d = 1 - sqrt(self.meat['dist'])/cfg.SENSOR_RANGE
        rock_l = -round((self.rock['ang']/(self.semiwide)), 1)
        rock_r = round((self.rock['ang']/(self.semiwide)), 1)
        rock_d = 1 - sqrt(self.rock['dist'])/cfg.SENSOR_RANGE
        enemy_l = clamp(enemy_l, 0, 1)
        enemy_r = clamp(enemy_r, 0, 1)
        plant_l = clamp(plant_l, 0, 1)
        plant_r = clamp(plant_r, 0, 1)
        meat_l = clamp(meat_l, 0, 1)
        meat_r = clamp(meat_r, 0, 1)
        rock_l = clamp(rock_l, 0, 1)
        rock_r = clamp(rock_r, 0, 1)
        return [enemy_l, enemy_r, enemy_d, plant_l, plant_r, plant_d, meat_l, meat_r, meat_d, rock_l, rock_r, rock_d]

    def set_detection_color(self, detection: bool):
        if detection:
            self.active_color = self.seeing_color
        else:
            self.active_color = self.base_color

    def draw(self, screen: Surface, camera: Camera, rel_position: Vector2, selected: bool=False, eye_color: Color=Color('skyblue')):
        r = int(self.radius)
        s = self.body.size
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        v2 = (cos(self.body.angle+1)*(s*0.85), sin(self.body.angle+1)*(s*0.85))
        v3 = (cos(self.body.angle-1)*(s*0.85), sin(self.body.angle-1)*(s*0.85))
        if selected:
            w1 = (int(cos(self.body.angle-self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle-self.semiwide)*(r+r*self.offset2[1])))
            w2 = (int(cos(self.body.angle+self.semiwide)*(r+r*self.offset2[0])), int(sin(self.body.angle+self.semiwide)*(r+r*self.offset2[1])))
            gfxdraw.arc(screen, x0, y0, r, int(degrees(self.body.angle-self.semiwide)), int(degrees(self.body.angle+self.semiwide)), self.active_color)
            gfxdraw.line(screen, x0, y0, x0+w1[0], y0+w1[1], self.active_color)
            gfxdraw.line(screen, x0, y0, x0+w2[0], y0+w2[1], self.active_color)    
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
            if self.rock['target'] != None:
                target = self.rock['target']
                rel_target_pos = camera.rel_pos(target.position)
                xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
                gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(175, 175, 175, 150))
                gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(175, 175, 175, 150))
        gfxdraw.aacircle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/9+1), eye_color)
        gfxdraw.filled_circle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/9+1), eye_color)
        gfxdraw.aacircle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/9+1), eye_color)
        gfxdraw.filled_circle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/9+1), eye_color)

    def new_observation(self) -> bool:
        if not self.observe:
            self.set_detection_color(detection=False)
            self.reset_detection()
            self.reset_range()
            self.allow_observe(True)
            return False
        elif self.observe_done:
            self.allow_observe(False)
            return True

    def reset_observation(self):
        self.observe_done = False
