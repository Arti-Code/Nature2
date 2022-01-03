from ast import Pass
from copy import copy, deepcopy
from random import random, randint
from math import log, sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
from statistics import mean
import pygame.gfxdraw as gfxdraw
from pygame.draw import polygon
from pygame import Surface, Color, Rect
from pygame.font import Font
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform, po
from lib.life import Life
from lib.math2 import flipy, clamp
from lib.sensor import Sensor
from lib.net import Network
from lib.species import random_name, modify_name
from lib.config import cfg
from lib.utils import log_to_file
from lib.camera import Camera

class Agent(Body):

    def __init__(self, screen: Surface, space: Space, collision_tag: int, position: tuple, genome: dict=None):
        super().__init__(body_type=Body.KINEMATIC)
        if position is not None:
            self.position = Vec2d(position[0], position[1])
        else:
            x = randint(50, cfg.WORLD[0]-50)
            y = randint(50, cfg.WORLD[1]-50)
            self.position = Vec2d(x, y)
        space.add(self)
        self.screen = screen
        self.angle = random()*2*PI
        self.body = Corpus(self, 50, 4, 40, 0.25)
        space.add(self.body)

    def update(self, dt: float):
        pass

    def draw(self, screen: Surface, camera: Camera) -> bool:
        if not camera.rect_on_screen(self.body.bb):
            return False
        t = int(self.shape.radius)
        pts = []
        for p in self.points:
            rel_pts = camera.rel_pos(Vector2(p[0], p[1]))
            pts.append((rel_pts.x, rel_pts.y))
        polygon(screen, Color('green'), pts, 0)
        polygon(screen, Color('yellowgreen'), pts, 3)
        return True

    def kill(self, space: Space):
        space.remove(self.body)
        space.remove(self)


class Corpus(Poly):

    def __init__(self, body: Body, length: int, segments: int, width: int, deviation: float):
        pts = []
        segment_x = int(length/segments)
        for s in range(segments):
            w = width
            w += w * (random()*2)-1 * deviation
            y = Vec2d(s*segment_x, w)
            p = y
            pts.append(p)
        seg_id = len(pts)-1
        for s in range(segments, 2*segments-1, 1):
            p = pts[seg_id]
            seg_id -= 1
            p2 = Vec2d(p.x, -p.y)
            pts.append(p2)
        #center = Vec2d(int(length/2), 0)
        center = Transform(tx=-int(length/2), ty=0)
        super().__init__(body=body, vertices=pts, transform=center, radius=1)
        