from random import random, randint
from math import sin, cos, radians, degrees, pi as PI, floor
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
        self.collision_type = 4
        self.sensor = True
        self.base_color = Color(255, 255, 255, 75)
        self.seeing_color = Color(255, 0, 0, 200)
        self.active_color = self.base_color
        self.reset_detection()
        self.description = description

    def reset_detection(self):
        self.detection = {
            'ang': 0,
            'dist': 500,
            'agent': False,
            'meat': False,
            'plant': False,
            'target': None
        }

    def add_detection(self, angle: float, dist: float, target: Body, type: str):
        if self.detection['dist'] > dist and self.wide/2 >= abs(angle):
            self.detection = {
                'ang': angle,
                'dist': dist,
                'agent': False,
                'meat': False,
                'plant': False,
                'target': target
            }
            if type == 'creature':
                self.detection['agent'] = True
            elif type == 'plant':
                self.detection['plant'] = True
            elif type == 'meat':
                self.detection['meat'] = True

    def get_detection(self) -> list:
        ang_l = round((self.detection['ang']/(self.wide/2)), 1)
        ang_r = round((self.detection['ang']/(self.wide/2)), 1)
        if ang_r < 0:
            ang_r = 0
        else:
            ang_r = 1 - ang_r
        if ang_l > 0:
            ang_l = 0
        else:
            ang_l = 1 + ang_l
        dist = self.detection['dist']/cfg.SENSOR_RANGE
        creature = self.detection['agent']
        plant = self.detection['plant']
        meat = self.detection['meat']
        return [ang_l, ang_r, dist, int(creature), int(plant), int(meat)]
    
    def set_detection_color(self, detection: bool):
        if detection:
            self.active_color = self.seeing_color
        else:
            self.active_color = self.base_color

    def draw(self, screen: Surface, camera: Camera, rel_position: Vector2):
        if self.detection['target'] != None:
            self.set_detection_color(detection=True)
        r = int(self.radius)
        w1 = (int(cos(self.body.angle-self.wide/2)*(r+r*self.offset2[0])), int(sin(self.body.angle-self.wide/2)*(r+r*self.offset2[1])))
        w2 = (int(cos(self.body.angle+self.wide/2)*(r+r*self.offset2[0])), int(sin(self.body.angle+self.wide/2)*(r+r*self.offset2[1])))
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        v = self.body.rotation_vector * r
        x = x0 + v.x; y = y0 + v.y
        s = self.body.size
        v2 = (cos(self.body.angle+1)*s, sin(self.body.angle+1)*s)
        v3 = (cos(self.body.angle-1)*s, sin(self.body.angle-1)*s)
        gfxdraw.arc(screen, x0, y0, r, int(degrees(self.body.angle-self.wide/2)), int(degrees(self.body.angle+self.wide/2)), self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w1[0], y0+w1[1], self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w2[0], y0+w2[1], self.active_color)
        gfxdraw.aacircle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.aacircle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        if self.detection['target'] != None:
            target = self.detection['target']
            rel_target_pos = camera.rel_pos(target.position)
            xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
            gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(56, 255, 245, 150))
            gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(56, 255, 245, 150))
        self.set_detection_color(detection=False)
        self.reset_detection()