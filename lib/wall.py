from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame.draw import line, lines
from pygame import Surface, Color, Rect
from pygame.math import Vector2
import pymunk as pm
from pymunk import Segment, Body, Space
from lib.math2 import flipy
from lib.camera import Camera


class Wall(Body):

    def __init__(self, screen: Surface, space: Space, p1: tuple, p2: tuple, thickness: float, border_color: Color, fill_color: Color):
        super().__init__(body_type=Body.STATIC)
        #self.screen = screen
        self.border_color = border_color
        self.fill_color = fill_color
        self.shape = Segment(self, p1, p2, thickness)
        self.shape.collision_type = 8
        #self.rect = Rect(min([p1[0], p2[0]]), min([p1[1], p2[1]]), )
        space.add(self, self.shape)
        #self.shape.update()
        bb = self.shape.bb
        self.rect = Rect(bb.left, bb.bottom, int(bb.right-bb.left), int(bb.top-bb.bottom))

    def draw(self, screen: Surface, camera: Camera):
        if not camera.rect_on_screen(self.rect):
            return False
        t = int(self.shape.radius)
        p1 = self.shape.a
        p2 = self.shape.b
        x1 = int(p1[0]); y1 = int(p1[1])
        x2 = int(p2[0]); y2 = int(p2[1])
        rel_p1 = camera.rel_pos(Vector2(x1, y1))
        rel_p2 = camera.rel_pos(Vector2(x2, y2))
        line(screen, self.border_color, (rel_p1.x, rel_p1.y), (rel_p2.x, rel_p2.y), t)

    def update(self, dT:float) -> None:
        pass

    def kill(self, space: Space) -> None:
        space.remove(self.shape)
        space.remove(self)