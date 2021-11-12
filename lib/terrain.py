from statistics import mean
import pygame
from pygame import image, Color, Surface
import pymunk
import pymunk.autogeometry
import pymunk.pygame_util
from pymunk import BB, Poly, Space, Shape
from lib.config import cfg
from lib.math2 import clamp


def generate_terrain(surface: Surface, space: Space, channel: int, mod_a: float, mod_b: int, collision_type: int, debug_color: Color) -> list[Shape]:
    lands = []
    for s in space.shapes:
        if hasattr(s, "generated") and s.generated:
            space.remove(s)

    def sample_func(point: tuple) -> float:
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            return int(color[channel]*mod_a+mod_b)
        except Exception as e:
            print(e)
            return 0

    line_set = pymunk.autogeometry.march_soft(BB(0, 0, 5999, 3999), int(600), int(400), 90, sample_func)
        #BB(0, 0, cfg.WORLD[0]-1, cfg.WORLD[1]-1), int(cfg.WORLD[0]/1), int(cfg.WORLD[1]/1), 90, sample_func)

    for polyline in line_set:
        verts = pymunk.autogeometry.simplify_curves(polyline, 0.8)
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

