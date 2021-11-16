from statistics import mean
import pygame
from pygame import image, Color, Surface
import pymunk
import pymunk.autogeometry
import pymunk.pygame_util
from pymunk import BB, Poly, Space, Shape
from lib.config import cfg
from lib.math2 import clamp


def generate_terrain_blue(surface: Surface, space: Space, channel: int, mod_a: float, mod_b: int, collision_type: int, debug_color: Color) -> list[Shape]:
    lands = []
    #for s in space.shapes:
    #    if hasattr(s, "generated") and s.generated:
    #        space.remove(s)

    def sample_func1(point: tuple) -> float:
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            res = int(color.b/2.55)
            return res
            #return int(color.hsla[2]/2.4)
        except Exception as e:
            print(e)
            return 0

    line_set = pymunk.autogeometry.march_soft(BB(0, 0, 1799, 899), int(180), int(90), 90, sample_func1)
        #BB(0, 0, cfg.WORLD[0]-1, cfg.WORLD[1]-1), int(cfg.WORLD[0]/1), int(cfg.WORLD[1]/1), 90, sample_func)

    for polyline in line_set:
        verts = pymunk.autogeometry.simplify_curves(polyline, 1.0)
        decompose_verts = pymunk.autogeometry.convex_decomposition(verts, 1)
        for hull_verts in decompose_verts:
            land = Poly(space.static_body, hull_verts, None, 0.6)
            land.friction = 0.5
            land.collision_type = collision_type
            land.color = debug_color
            land.generated = True
            space.add(land)
            lands.append(land)
    return lands

def generate_terrain_red(surface: Surface, space: Space, channel: int, mod_a: float, mod_b: int, collision_type: int, debug_color: Color) -> list[Shape]:
    lands = []
    #for s in space.shapes:
    #    if hasattr(s, "generated") and s.generated:
    #        space.remove(s)

    def sample_func2(point: tuple) -> float:
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            #return int(color[channel]*mod_a+mod_b)
            #hsla = color.hsla()
            res = int((color.r+color.g+color.b)/3)
            return res
        except Exception as e:
            print(e)
            return 0

    line_set = pymunk.autogeometry.march_soft(BB(0, 0, 1799, 899), int(180), int(90), 90, sample_func2)
        #BB(0, 0, cfg.WORLD[0]-1, cfg.WORLD[1]-1), int(cfg.WORLD[0]/1), int(cfg.WORLD[1]/1), 90, sample_func)

    for polyline in line_set:
        verts = pymunk.autogeometry.simplify_curves(polyline, 1.0)
        decompose_verts = pymunk.autogeometry.convex_decomposition(verts, 1)
        for hull_verts in decompose_verts:
            land = Poly(space.static_body, hull_verts, None, 0.6)
            land.friction = 0.5
            land.collision_type = collision_type
            land.color = debug_color
            land.generated = True
            space.add(land)
            lands.append(land)
    return lands