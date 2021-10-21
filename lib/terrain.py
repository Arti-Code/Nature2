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
from perlin_noise import PerlinNoise
from enum import IntEnum

class TerrainLevels(IntEnum):
    DEEP_WATER  = 0
    WATER       = 1
    SHORE       = 2
    LOW_LAND    = 3
    LAND        = 4
    HILLS       = 5
    MOUNTAIN    = 6
    SNOW_PEAK   = 7


class Terrain():

    def __init__(self, res: int, size: tuple):
        self.map = []
        self.size = size
        self.res = res
        self.terrain = self.generate_perlin_map(size, res)
        self.gfx_terrain = self.redraw_terrain(self.terrain, res, size)

    def generate_perlin_map(self, size: tuple, res: int) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=10)
        noise2 = PerlinNoise(octaves=16)
        x_res, y_res = (int(size[0]/res), int(size[1]/res))
        for y in range(y_res):
            row = []
            for x in range(x_res):
                pix = noise1([x/x_res, y/y_res])
                pix += 0.5 * noise2([x/x_res, y/y_res])
                row.append(pix)
            terrain.append(row)
        return terrain

    def redraw_terrain(self, terrain: list, resolution: int, size: tuple) -> Surface:
        gfx_terrain = Surface(size=size)
        for y in range(len(terrain)-1):
            for x in range(len(terrain[y])-1):
                color = Color('white')
                if terrain[y][x] < -0.5:
                    color = Color('darkblue')
                elif terrain[y][x] < -0.2:
                    color = Color('blue')
                elif terrain[y][x] < 0:
                    color = Color('yellow')
                elif terrain[y][x] < 0.3:
                    color = Color('green')
                elif terrain[y][x] < 0.6:
                    color = Color('brown')
                else:
                    color = Color('grey')
                rect = Rect(y*resolution, x*resolution, resolution, resolution)
                gfxdraw.box(gfx_terrain, rect, color)
        return gfx_terrain

    def get_map(self) -> Surface:
        return self.gfx_terrain
