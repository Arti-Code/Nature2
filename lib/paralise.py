from enum import Enum
from math import cos, degrees, sin, sqrt

import pygame.gfxdraw as gfxdraw
from pygame import Color, Surface
from pygame.math import Vector2
from pymunk import Body, Circle, Vec2d

from lib.camera import Camera
from lib.config import cfg
from lib.math2 import clamp
from lib.species import brotherhood



class Paralise(Circle):

    def __init__(self, body: Body, radius: int, wide: float) -> None:
        super().__init__(body, radius)
        self.wide = wide
        self.semiwide = wide/2
        self.collision_type = 4
        self.sensor = True
        self.base_color = Color(255, 255, 255, 75)