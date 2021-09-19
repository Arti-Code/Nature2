from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame.draw import line, lines, polygon
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Segment, Poly, Body, Space
from lib.math2 import flipy
from lib.camera import Camera
from pygame.math import Vector2

class Rock(Body):

    def __init__(self, screen: Surface, space: Space, vertices: list, thickness: float, border_color: Color, fill_color: Color):
        super().__init__(body_type=Body.STATIC)
        #self.screen = screen
        self.border_color = border_color
        self.fill_color = fill_color
        self.vertices = vertices
        self.shape = Poly(self, vertices, None, thickness)
        self.shape.collision_type = 8
        space.add(self, self.shape)
        self.points = []
        x_axe = []
        y_axe = []
        for vert in self.shape.get_vertices():
            self.points.append((int(vert[0]), flipy(int(vert[1]))))
            x_axe.append((int(vert[0])))
            y_axe.append(flipy(int(vert[1])))
        x_min = min(x_axe)
        x_max = max(x_axe)
        y_min = min(y_axe)
        y_max = max(y_axe)
        self.rect = Rect(x_min, y_min, x_max-x_min, y_max-y_min)

    def draw(self, screen: Surface, camera: Camera) -> bool:
        #p1 = self.shape.a
        #p2 = self.shape.b
        #x1 = int(p1[0]); y1 = int(p1[1])
        #x2 = int(p2[0]); y2 = int(p2[1])
        #line(screen, self.border_color, (x1, flipy(y1)), (x2, flipy(y2)), t)
        if not camera.rect_on_screen(self.rect):
            return False
        t = int(self.shape.radius)
        pts = []
        for p in self.points:
            rel_pts = camera.rel_pos(Vector2(p[0], p[1]))
            pts.append((rel_pts.x, rel_pts.y))
        polygon(screen, self.border_color, pts, 0)
        polygon(screen, Color('gray'), pts, 3)
        return True

    def update(self, dT:float) -> None:
        pass

    def kill(self, space: Space) -> None:
        space.remove(self.shape)
        space.remove(self)
