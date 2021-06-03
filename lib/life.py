from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.math2 import flipy, ang2vec, ang2vec2, clamp

class Detector():

    def __init__(self, screen: Surface, body: Body, collision_type: any, degree_angle: int, length: int):
        self.screen = screen
        self.body = body
        self.angle = degree_angle
        self.length = length
        x2, y2 = ang2vec2(radians(degree_angle))
        b = (x2*length, y2*length)
        self.shape = Segment(body=body, a=(0,0), b=b, radius=3)
        self.shape.collision_type = collision_type
        self.shape.sensor = True
        self.color = Color('white')

    def draw(self):
        p1 = (self.shape.body.position.x, self.shape.body.position.y)
        rv = (self.body.rotation_vector.rotated_degrees(self.angle))*self.length
        p2 = (p1[0]+rv[0], p1[1]+rv[1])
        color_edge = self.color
        color_edge.a = 125
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]-1), flipy(int(p2[1]-1)), self.color)
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]), flipy(int(p2[1])), self.color)
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]+1), flipy(int(p2[1]+1)), self.color)
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]-2), flipy(int(p2[1]-2)), color_edge)
        gfxdraw.line(self.screen, int(p1[0]), flipy(int(p1[1])), int(p2[0]+2), flipy(int(p2[1]+2)), color_edge)

    def set_color(self, color: Color):
        self.color = color

    def change_angle(self, delta_rad: float):
        self.angle = self.angle + delta_rad
        self.angle = clamp(self.angle, -120, 120)
        x2, y2 = ang2vec2(radians(self.angle))
        b = (x2*self.length, y2*self.length)
        #self.shape.b = b
        self.shape.unsafe_set_endpoints((0, 0), b)


class PolyDetector():

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
        #vertex = self.shape.get_vertices()
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
        #x1, y1 = ang2vec2(radians((self.angle+self.radial_width/2)%360))
        #x2, y2 = ang2vec2(radians((self.angle-self.radial_width/2)%360))
        #v0 = (0, 0)
        #v1 = (x1*self.length, y1*self.length)
        #v2 = (x2*self.length, y2*self.length)
        #verts = [v0, v1, v2]
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


class Life(Body):

    def __init__(self, screen: Surface, space: Space, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, angle: float=None, visual_range: int=180, position: Vec2d=None):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.screen = screen
        self.color0 = color0
        self.color1 = color1
        self.color2 = color2
        self.detectors = []
        self.eye_colors = {}
        self.visual_range = visual_range
        #self.body = Body(body_type=Body.KINEMATIC)
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
        self.detectors = []
        self.detectors.append(PolyDetector(screen, self, 4, 0, 6, 300, 0, 0))
        space.add(self.detectors[0].shape)
        self.detectors.append(PolyDetector(screen, self, 4, 45, 10, 300, 0, 125))
        space.add(self.detectors[1].shape)
        self.detectors.append(PolyDetector(screen, self, 4, -45, 10, 300, -125, 0))
        space.add(self.detectors[2].shape)

    def draw(self):
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        rot = self.rotation_vector
        self.draw_detectors()
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r), self.color0)
        gfxdraw.filled_circle(self.screen, int(x), flipy(int(y)), int(r-2), self.color1)
        if r > 2:
            x2 = round(x + rot.x*r)
            y2 = round(y + rot.y*r)
            r2 = round(r/2)
            gfxdraw.filled_circle(self.screen, x2, flipy(y2), r2, self.color2)
        self.color0 = Color('green')

    def draw_detectors(self):
        for detector in self.detectors:
            detector.draw()

    def update(self, space: Space, dt:float, detections: list=[]) -> None:
        self.update_detections(detections)
        self.random_move(space, dt)

    def update_detections(self, detections: list):        
        for detector in self.detectors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def random_move(self, space: Space, dt: float) -> None:
        speed: float; rot_speed: float; move: float; turn: float
        speed = 1; rot_speed = 0.02
        move = random()*speed
        turn = random()*2-1
        look = (random()*2-1)*4
        self.angle = (self.angle+(turn*rot_speed))%(2*PI)
        self.vdir = self.rotation_vector
        self.velocity = move*self.vdir/dt
        self.detectors[1].rotate(look)
        self.detectors[2].rotate(-look)
       
