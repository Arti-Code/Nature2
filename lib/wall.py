from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame.draw import line, lines
from pygame import Surface, Color, Rect
from pygame.math import Vector2
from lib.math2 import flipy
from lib.camera import Camera


class Wall:

    def __init__(self, p1: tuple, p2: tuple, thickness: float, border_color: Color, fill_color: Color):
        self.border_color = border_color
        self.fill_color = fill_color
        self.shape: tuple(tuple, tuple) = (p1, p2)
        self.rect = Rect(min([p1[0], p2[0]])+3, min([p1[1], p2[1]])+3, max([p1[0], p2[0]]), max([p1[1], p2[1]]))
        #self.rect = Rect(bb.left, bb.bottom, int(bb.right-bb.left), int(bb.top-bb.bottom))

    def draw(self, screen: Surface, camera: Camera):
        if not camera.rect_on_screen(self.rect):
            return False
        #t = int(self.shape.radius)
        p1 = self.shape[0]
        p2 = self.shape[1]
        x1 = int(p1[0]); y1 = int(p1[1])
        x2 = int(p2[0]); y2 = int(p2[1])
        rel_p1 = camera.rel_pos(Vector2(x1, y1))
        rel_p2 = camera.rel_pos(Vector2(x2, y2))
        #t = min([abs(rel_p1.x-rel_p2.x), abs(rel_p1.y-rel_p2.y)])
        line(screen, self.border_color, (rel_p1.x, rel_p1.y), (rel_p2.x, rel_p2.y), int(1))

    def update(self, dT:float):
        pass

    def kill(self):
        pass