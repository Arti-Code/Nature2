from random import random, randint
from math import sin, cos, pi as PI
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Segment, Body
from lib.math2 import flipy


class Wall():

    def __init__(self, screen: Surface, p1: tuple, p2: tuple, thickness: float, border_color: Color, fill_color: Color):
        self.screen = screen
        self.border_color = border_color
        self.fill_color = fill_color
        self.body = Body()
        self.body.body_type = Body.STATIC
        self.shape = Segment(self.body, p1, p2, thickness)
        self.shape.collision_type = 2

    def get_body_and_shape(self) -> tuple:
        return (self.body, self.shape)

    def get_point1(self) -> tuple:
        return self.shape.a

    def get_point2(self) -> tuple:
        return self.shape.b

    def get_thickness(self) -> float:
        return self.shape.radius

    def draw(self):
        # * -=VARs=-
        x1: int; y1: int; x2: int; y2: int; t: int
        t = int(self.get_thickness())
        p1 = self.get_point1()
        p2 = self.get_point2()
        x1 = int(p1[0]); y1 = int(p1[1])
        x2 = int(p2[0]); y2 = int(p2[1])
        # * -=DRAW WALL AS SINGLE LINE=- *
        gfxdraw.line(self.screen, x1, flipy(y1), x2, flipy(y2), self.border_color)

    def update(self, dT:float) -> None:
        pass


