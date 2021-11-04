from random import random, randint
from math import sin, cos, pi as PI
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

    def draw(self, surface: Surface, water_level: float=0.4):
        if self.occupied:
            gfxdraw.rectangle(surface, self, Color('yellow'))
            return
        water_level = clamp(water_level, 0.0, 1.0)
        height = self.depth
        #height = round((height+1), 1)
        #water = water_level - height
        color = Color(0, 0, 0)
        if self.water <= 0.0:
            color = Color(int(75+154*height), int(75+154*height), int(75+154*height))
        elif self.water <= 0.2:
            color = Color(int(100), int(100), int(184+70*self.water))
            #self.water = 1
        elif self.water <= 0.4:
            color = Color(int(20), int(20), int(200+50*self.water))
        else:
            color = Color(int(10), int(10), int(100+100*self.water))
            #self.water = 1
        gfxdraw.box(surface, self, color)
        #if c2 > water_level:
        #    height = c2
        #    color = Color(int(255*c2), int(255*c2), int(255*c2))
        #else:
        #    depth = (c2*200)/water_level
        #    color = Color(0, 0, int(35+depth))
        #gfxdraw.box(surface, self, color)
        #gfxdraw.rectangle(surface, self, Color('gray'))

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

    #def get_tiles_arround(self) -> list:
    #    x = self.position.x, y=self.position.y
    #    tiles = list(
    #        (x-1, y-1), (x, y-1), (x+1, y-1)
    #        (x-1, y), (x+1, y)
    #        (x-1, y+1), (x, y+1), (x+1, y+1)
    #    )
    #    return tiles
#
    #def update(self, water: list):
        pass

class Terrain():

    def __init__(self, world_size: tuple, res: int, water_lvl: float, octaves: tuple=(5, 12)):
        self.map = []
        #self.water = []
        self.tiles = []
        self.world_size = world_size
        self.res = res
        self.terrain = self.generate_perlin_map(world_size, res, water_lvl, octaves)
        #self.gfx_terrain = self.redraw_terrain(self.terrain, res, world_size)

    def generate_perlin_map(self, world_size: tuple, res: int, water_lvl: float=0.3, octaves: tuple=(4, 6)) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=octaves[0])
        noise2 = PerlinNoise(octaves=octaves[1])
        #noise3 = PerlinNoise(octaves=14)
        x_axe, y_axe = (int(world_size[0]/res), int(world_size[1]/res))
        for y in range(y_axe):
            row = []
            tiles_row = []
            #water_row = []
            for x in range(x_axe):
                pix = noise1([x/x_axe, y/y_axe])
                pix += 0.5 * noise2([x/x_axe, y/y_axe])
                height = round(pix, 1)
                row.append(height)
                water_edge = round(water_lvl-height, 1)
                water_edge = clamp(water_edge, 0, 1)
                tile = Tile(x, y, res, res, height, water_edge)
                #water = water_lvl-height
                tiles_row.append(tile)
                #water_row.append(water)
            terrain.append(row)
            #self.water.append(water_row)
            self.tiles.append(tiles_row)
        return terrain

    def draw_tiles(self) -> Surface:
        terrain = Surface(self.world_size)
        for y_tiles in self.tiles:
            for tile in y_tiles:
                tile.draw(terrain, 0.4)
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
class Terrain2():

    def __init__(self):
        self.terrain_surface: Surface=None

    def generate(self, space: Space, world_size: tuple, res: int):
        noise_list = [(4, 1.0), (8, 0.5)]
        noise_map = self.make_noise_map(world_size, res, noise_list)
        self.terrain_surface = self.draw_terrain(noise_map, res, world_size)
        self.generate_physic_terrain(space, world_size)

    def make_noise_map(self, world_size: tuple, res: int, noise_list: list[tuple]) -> list:
        """@param: noise_list: list of single noises described as tuple of octaves: int, influence: float between 0.0 - 1.0"""
        terrain = []
        noises = []
        for noise_params in noise_list:
            octaves = noise_params[0]
            influence = noise_params[1]
            noise = PerlinNoise(octaves=octaves)
            noises.append((noise, influence))

        x_dim, y_dim = (int(world_size[0]/res), int(world_size[1]/res))
        for y in range(y_dim):
            row = []
            for x in range(x_dim):
                pix = 0
                for noise, influence in noises:
                    pix += influence * noise([x/x_dim, y/y_dim])
                row.append(pix)
            terrain.append(row)
        return terrain

    def draw_terrain(self, terrain: list, resolution: int, world_size: tuple) -> Surface:
        surface_terrain = Surface(world_size)
        for y in range(len(terrain)-1):
            for x in range(len(terrain[y])-1):
                h = terrain[y][x]
                height = round((h+1)/2, 1)
                color = Color(0, 0, 0)
                if height > 0.85:
                    color = Color(int(255*0.1), int(255*0.1), int(255*0.1))
                #elif height < 0.5:
                #    color = Color(int(255*0.4), int(255*0.4), int(255*0.4))
                #elif height < 0.9:
                #    color = Color(int(255*0.7), int(255*0.7), int(255*0.7))
                else:
                    color = Color(int(255), int(255), int(255))
                rect = Rect(y*resolution, x*resolution, resolution, resolution)
                gfxdraw.box(surface_terrain, rect, color)
        return surface_terrain

    def sample_func(self, point):
        try:
            p = int(point[0]), int(flipy(point[1]))
            color = self.terrain_surface.get_at(p)
            #return color.hsla[2]
            return int(mean([color.r, color.g, color.b]))
        except Exception as e:
            print(e)
            return 0

    def generate_physic_terrain(self, space: Space, world_size: tuple):
        line_set = autogeometry.march_hard(BB(0, 0, world_size[0]-1, world_size[1]-1), int(world_size[0]/10), int(world_size[1]/10), 25, self.sample_func)
        for polyline in line_set:
            line = autogeometry.simplify_curves(polyline, 0.25)
            poly = Poly(space.static_body, autogeometry.to_convex_hull(line, 0.5))
            poly.collision_type = 8
            space.add(poly)

