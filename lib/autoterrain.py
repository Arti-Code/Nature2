import os
import sys
from time import time
from math import degrees, hypot
from statistics import mean
from random import randint, random
from typing import Union
import pygame
from pygame import Color, Surface, image
from pygame.constants import K_n
from pygame.font import Font, match_font 
from pymunk import BB, Vec2d, Space, Segment, Body, Circle, Shape, Poly, autogeometry
import pymunk.pygame_util
#from lib.life import Life, Creature, Plant
from lib.wall import Wall
from lib.sensor import Sensor
from lib.math2 import set_world, world, flipy
from lib.config import *
from lib.manager import Manager
from lib.collisions import process_creature_plant_collisions, process_edge_collisions, process_creatures_collisions, detect_creature, detect_plant, detect_plant_end, detect_creature_end
#from lib.test import Test

class Terrain:

    def __init__(self, screen: Surface, space: Space, image_name: str, collision_tag: int, offset: tuple[int]=(0, 0)):
        self.terrain_surface = image.load(image_name)
        self.terrain_surface.convert_alpha()
        self.offset = offset
        self.screen = screen
        self.space = space
        self.collision_tag = collision_tag
        self.generate(terrain=self.terrain_surface, space=space)

    #def load_from_bw_bmp(self, image: str) -> Surface:
    #    return image.load_basic(image)

    def sample_func(self, point):
        try:
            p = int(point[0]), int(750-point[1])
            color = self.terrain_surface.get_at(p)
            return color.hsla[2]
        except Exception as e:
            print(e)
            return 0

    def generate(self, terrain: Surface, space: Space):
        line_set = autogeometry.march_hard(BB(0, 0, 1499, 749), 1500, 750, 50, self.sample_func)
        for polyline in line_set:
            line = autogeometry.simplify_curves(polyline, 0.1)
            poly = Poly(self.space.static_body, autogeometry.to_convex_hull(line, 1.0))
            poly.collision_type = 8
            self.space.add(poly)
            #for i in range(len(line) - 1):
            #    p1 = line[i]
            #    p2 = line[i + 1]
            #    shape = Segment(self.space.static_body, p1, p2, 2)
            #    shape.friction = 0.5
            #    shape.collision_type = self.collision_tag
            #    shape.color = pygame.Color("gray")
            #    shape.generated = True
            #    self.space.add(shape)

