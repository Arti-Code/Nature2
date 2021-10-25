from random import random, randint
from math import sin, cos, pi as PI
from statistics import mean
from lib.math2 import clamp
import pygame.gfxdraw as gfxdraw
from pygame.draw import line, lines, polygon
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Segment, Poly, Body, Space, autogeometry, BB
from lib.math2 import flipy
from lib.camera import Camera
from pygame.math import Vector2
from perlin_noise import PerlinNoise
from enum import IntEnum


class Tile(Rect):

    def __init__(self, l: int, t: int, w: int, h: int, depth: float):
        super().__init__(l*w, t*h, w, h)
        self.depth = depth

    def draw(self, surface: Surface, water_level: float=0.7):
        water_level = clamp(water_level, 0.0, 2.0)
        height = self.depth
        height = round((height+1), 1)
        color = Color(0, 0, 0)
        if height > water_level:
            color = Color(int(127*height), int(127*height), int(127*height))
        else:
            depth = (height*200)/water_level
            color = Color(int(80*(height/water_level)), int(80*(height/water_level)), int(50+depth))
        gfxdraw.box(surface, self, color)
        #if c2 > water_level:
        #    height = c2
        #    color = Color(int(255*c2), int(255*c2), int(255*c2))
        #else:
        #    depth = (c2*200)/water_level
        #    color = Color(0, 0, int(35+depth))
        #gfxdraw.box(surface, self, color)
        #gfxdraw.rectangle(surface, self, Color('gray'))


class Terrain():

    def __init__(self, world_size: tuple, res: int):
        self.map = []
        self.tiles = []
        self.world_size = world_size
        self.res = res
        self.terrain = self.generate_perlin_map(world_size, res)
        #self.gfx_terrain = self.redraw_terrain(self.terrain, res, world_size)

    def generate_perlin_map(self, world_size: tuple, res: int) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=4)
        noise2 = PerlinNoise(octaves=8)
        noise3 = PerlinNoise(octaves=12)
        x_res, y_res = (int(world_size[0]/res), int(world_size[1]/res))
        for y in range(y_res):
            row = []
            for x in range(x_res):
                pix = noise1([x/x_res, y/y_res])
                pix += 0.5 * noise2([x/x_res, y/y_res])
                pix += 0.25 * noise3([x/x_res, y/y_res])
                row.append(pix)
                tile = Tile(x, y, res, res, pix)
                self.tiles.append(tile)
            terrain.append(row)
        return terrain

    def generate_perlin_map2(self, world_size: tuple, res: int) -> list:
        terrain = []
        noise1 = PerlinNoise(octaves=4)
        noise2 = PerlinNoise(octaves=8)
        x_res, y_res = (int(world_size[0]/res), int(world_size[1]/res))
        for y in range(y_res):
            row = []
            for x in range(x_res):
                pix = noise1([x/x_res, y/y_res])
                pix += 0.5 * noise2([x/x_res, y/y_res])
                row.append(pix)
            terrain.append(row)
        return terrain

    def draw_tiles(self) -> Surface:
        terrain = Surface(self.world_size)
        for tile in self.tiles:
            tile.draw(terrain, 0.8)
        return terrain

    def redraw_terrain(self, terrain: list, resolution: int, world_size: tuple) -> Surface:
        gfx_terrain = Surface(world_size=world_size)
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
                rect = Rect(y*resolution, x*resolution, resolution, resolution)
                gfxdraw.box(gfx_terrain, rect, color)
        return gfx_terrain

    def get_map(self) -> Surface:
        return self.gfx_terrain


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