import pygame,sys
from pygame import Surface, Color, Rect
import pymunk
from pymunk import autogeometry, Poly, Space, BB
from pymunk.autogeometry import march_hard, march_soft
from pygame.locals import *
from lib.terrain import Terrain


def sample_func(point):
    try:
        p = int(point[0]), int(750-point[1])
        color = terrain_surface.get_at(p)
        return color.hsla[2]
    except Exception as e:
        print(e)
        return 0

def generate(terrain: Surface, space: Space):
    line_set = autogeometry.march_hard(BB(0, 0, 1499, 749), 1500, 750, 50, sample_func)
    for polyline in line_set:
        line = autogeometry.simplify_curves(polyline, 0.1)
        poly = Poly(space.static_body, autogeometry.to_convex_hull(line, 1.0))
        poly.collision_type = 8
        space.add(poly)


pygame.init()
screen = pygame.display.set_mode((1500,900))
pygame.display.set_caption("Test")
terrain = Terrain((900, 600), 10, 0.0, (4, 6))
screen.blit(terrain.draw_tiles(), (0, 0))
space = Space()
while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()