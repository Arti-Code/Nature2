import pygame
from pygame import image, Color, Surface
import pymunk
import pymunk.autogeometry
import pymunk.pygame_util
from pymunk import BB, Poly, Space, Shape
from lib.config import cfg


def generate_geometry(surface: Surface, space: Space) -> list[Shape]:
    lands = []
    for s in space.shapes:
        if hasattr(s, "generated") and s.generated:
            space.remove(s)

    def sample_func(point: tuple) -> float:
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            return int(color.g/2.55)
        except Exception as e:
            print(e)
            return 0

    line_set = pymunk.autogeometry.march_soft(
        BB(0, 0, cfg.WORLD[0]-1, cfg.WORLD[1]-1), int(cfg.WORLD[0]/5), int(cfg.WORLD[1]/5), 90, sample_func)

    for polyline in line_set:
        verts = pymunk.autogeometry.simplify_curves(polyline, 0.8)
        decompose_verts = pymunk.autogeometry.convex_decomposition(verts, 1)
        for hull_verts in decompose_verts:
            land = Poly(space.static_body, hull_verts, None, 0.6)
            land.friction = 0.5
            land.color = Color(200, 200, 200, 0)
            land.generated = True
            space.add(land)
            lands.append(land)
    return lands

