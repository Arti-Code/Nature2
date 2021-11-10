from random import random, randint
from math import sin, cos, pi as PI
from time import time
from statistics import mean
from lib.math2 import clamp
import pygame.gfxdraw as gfxdraw
from pygame.draw import line, lines, polygon
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Segment, Poly, Body, Space, autogeometry, BB
from lib.math2 import flipy, sort_by_water
from lib.camera import Camera
from pygame.math import Vector2
from perlin_noise import PerlinNoise
from enum import IntEnum
from typing import Union




class Tile(Rect):

    def __init__(self, l: int, t: int, w: int, h: int, depth: float, water: float=0.0):
        super().__init__(l*w, t*h, w, h)
        self.depth = depth
        self.evols = []
        self.occupied: bool= False
        self.water = water

    def draw(self, surface: Surface):
        if self.occupied:
            gfxdraw.rectangle(surface, self, Color('yellow'))
            return
        height = self.depth
        color = Color(0, 0, 0)
        if self.water <= 0.0:
            color = Color(int(50+154*height), int(75+154*height), int(75+154*height))
        elif self.water <= 0.1:
            color = Color(25, 50, int(255*(1.0-self.water)), 255)
        elif self.water <= 0.3:
            color = Color(0, 0, int(255*(1.0-self.water)), 250)
        elif self.water <= 0.4:
            color = Color(0, 0, int(255*(1.0-self.water)), 220)
        else:
            color = Color(0, 0, int(255*(1.0-self.water)), 180)
        gfxdraw.box(surface, self, color)

    def is_water(self) -> tuple:
        if self.water > 0:
            return (True, self.water)
        return (False, 0)

    def overlap(self, rect: Rect) -> bool:
        return self.colliderect(rect)

    def update(self):
        self.occupied = False


class Water(Rect):
    def __init__(self, l: int, t: int, w: int, h: int, depth: float, water_lvl: float):
        super().__init__(l*w, t*h, w, h)
        self.depth = depth
        self.position = (int((l*w)+0.5*w), int((t*h)+0.5*h))
        self.water_lvl = water_lvl

    def get_coord(self) -> tuple:
        return self.position

    def kill(self):
        self.kill()


class Terrain():

    def __init__(self, world_size: tuple, res: int, water_lvl: float, octaves: tuple=(5, 12)):
        self.map = []
        self.tiles = []
        self.world_size = world_size
        self.res = res
        self.water_lvl = water_lvl
        self.octaves = octaves
        self.terrain = self.generate_perlin_map(self.world_size, self.res, self.water_lvl, self.octaves)

    def generate_perlin_map(self, world_size: tuple, res: int, water_lvl: float=0.3, octaves: tuple=(4, 6)) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=octaves[0], seed=int((time()%int(time()))*10000))
        noise2 = PerlinNoise(octaves=octaves[1], seed=int((time()%int(time()))*10000))
        x_axe, y_axe = (int(world_size[0]/res), int(world_size[1]/res))
        for y in range(y_axe):
            row = []
            tiles_row = []
            for x in range(x_axe):
                pix = noise1([x/x_axe, y/y_axe])
                pix += 0.4 * noise2([x/x_axe, y/y_axe])
                height = round((pix+1)/2, 1)
                row.append(height)
                water_edge = round(water_lvl-height, 1)
                water_edge = clamp(water_edge, 0, 1)
                tile = Tile(x, y, res, res, height, water_edge)
                tiles_row.append(tile)
            terrain.append(row)
            self.tiles.append(tiles_row)
        return terrain

    def draw_tiles(self) -> Surface:
        terrain = Surface(self.world_size)
        for y_tiles in self.tiles:
            for tile in y_tiles:
                tile.draw(terrain)
        return terrain

    def draw_water(self) -> Surface:
        self.water.sort(ke=sort_by_water, reverse=True)

    def redraw_terrain(self, terrain: list, resolution: int, world_size: tuple, water_level: float) -> Surface:
        gfx_terrain = Surface(world_size=world_size)
        for y in range(len(terrain)-1):
            for x in range(len(terrain[y])-1):
                h = terrain[y][x]
                if h >= water_level:
                    color = Color(int(254*h), int(254*h), int(254*h))
                else:
                    d = water_level - h
                    if d <= 0.1:
                        color = Color(75, 75, int(155+100*d))
                    else:
                        color = Color(0, 0, int(100+154*d))
                rect = Rect(y*resolution, x*resolution, resolution, resolution)
                gfxdraw.box(gfx_terrain, rect, color)
        return gfx_terrain

    def get_map(self) -> Surface:
        return self.gfx_terrain

    def get_tile(self, coord: tuple) -> Tile:
        if coord[0] < len(self.tiles) and coord[0] >= 0 and coord[1] < len(self.tiles) and coord[1] >= 0:
            return self.tiles[coord[1]][coord[0]]
        return None
    
    def is_water_tile(self, coord: tuple) -> tuple:
        if coord[0] < len(self.tiles) and coord[0] >= 0 and coord[1] < len(self.tiles) and coord[1] >= 0:
            return self.tiles[coord[1]][coord[0]].is_water()
        return (False, 0)

    def set_occupied(self, coord: tuple, state: bool=True):
        if coord[0] < len(self.tiles) and coord[0] >= 0 and coord[1] < len(self.tiles) and coord[1] >= 0:
            self.tiles[coord[1]][coord[0]].occupied = state

    def update(self):
        for y_tiles in self.tiles:
            for tile in y_tiles:
                tile.update()

    def detect_water(self, sensor_rect: Rect, p0: tuple, p1: tuple) -> bool:
        l = round(sensor_rect.left/self.res)
        t = round(sensor_rect.top/self.res)
        w = round(sensor_rect.width/self.res)
        h = round(sensor_rect.height/self.res)
        for y in range(t, t+h-1):
            for x in range(l, l+w-1):
                tile = self.get_tile((x, y))
                if not tile is None:
                    if tile.is_water():
                        if tile.clipline(p0, p1):
                            return True
        return False

    def detect_water2(self, position: tuple) -> bool:
        title = self.get_tile(position)
        if title.is_water(): return True
        return False