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


class Tile(Rect):

    def __init__(self, l: int, t: int, w: int, h: int, depth: float):
        super().__init__(l*w, t*h, w, h)
        self.depth = depth

    def draw(self, surface: Surface):
        c = self.depth
        c2 = round((c+1)/2, 1)
        color = Color(0, 0, 0)
        if c2 > 0.4:
            color = Color(int(255*c2), int(255*c2), int(255*c2))
        else:
            color = Color(0, 0, int(155+100*c2))
        gfxdraw.box(surface, self, color)
        gfxdraw.rectangle(surface, self, Color('black'))


class Terrain():

    def __init__(self, res: int, size: tuple):
        self.map = []
        self.tiles = []
        self.size = size
        self.res = res
        self.terrain = self.generate_perlin_map(size, res)
        #self.gfx_terrain = self.redraw_terrain(self.terrain, res, size)

    def generate_perlin_map(self, size: tuple, res: int) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=4)
        noise2 = PerlinNoise(octaves=8)
        x_res, y_res = (int(size[0]/res), int(size[1]/res))
        for y in range(y_res):
            row = []
            for x in range(x_res):
                pix = noise1([x/x_res, y/y_res])
                pix += 0.5 * noise2([x/x_res, y/y_res])
                row.append(pix)
                tile = Tile(x, y, res, res, pix)
                self.tiles.append(tile)
            terrain.append(row)
        return terrain

    def generate_perlin_map2(self, size: tuple, res: int) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=4)
        noise2 = PerlinNoise(octaves=8)
        x_res, y_res = (int(size[0]/res), int(size[1]/res))
        for y in range(y_res):
            row = []
            for x in range(x_res):
                pix = noise1([x/x_res, y/y_res])
                pix += 0.5 * noise2([x/x_res, y/y_res])
                row.append(pix)
            terrain.append(row)
        return terrain

    def draw_tiles(self) -> Surface:
        terrain = Surface(self.size)
        for tile in self.tiles:
            tile.draw(terrain)
        return terrain

    def redraw_terrain(self, terrain: list, resolution: int, size: tuple) -> Surface:
        gfx_terrain = Surface(size=size)
        for y in range(len(terrain)-1):
            for x in range(len(terrain[y])-1):
                c = terrain[y][x]
                c2 = round((c+1)/2, 1)
                color = Color(0, 0, 0)
                #if c2 > 0.4 and c2 < 0.7:
                #    c2 = 0.5
                if c2 > 0.4:
                    color = Color(int(255*c2), int(255*c2), int(255*c2))
                else:
                    color = Color(0, 0, int(155+100*c2))
                #color = Color('white')
                #if terrain[y][x] < -0.5:
                #    color = Color('darkblue')
                #elif terrain[y][x] < -0.2:
                #    color = Color('blue')
                #elif terrain[y][x] < 0:
                #    color = Color('yellow')
                #elif terrain[y][x] < 0.3:
                #    color = Color('green')
                #elif terrain[y][x] < 0.6:
                #    color = Color('brown')
                #else:
                #    color = Color('grey')
                rect = Rect(y*resolution, x*resolution, resolution, resolution)
                gfxdraw.box(gfx_terrain, rect, color)
        return gfx_terrain

    def get_map(self) -> Surface:
        return self.gfx_terrain
