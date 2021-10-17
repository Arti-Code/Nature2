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
from perlin_noise import PerlinNoise as Noise


class Terrain():

    def __init__(self, xy_res: tuple, xy_size: tuple):
        self.map = []
        self.xy_size = xy_size
        self.xy_res = xy_res

    def generate_map(self, resolution: tuple):
        self.map = []
        x_res, y_res = resolution
        for y in range(y_res):
            for x in range(x_res):
                

