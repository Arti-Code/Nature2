import sys
from random import random, randint
import pygame
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
from lib.life import Life
from lib.wall import Wall
from lib.math2 import flipy

def init(view_size: tuple):
    pygame.init()
    global screen
    screen = pygame.display.set_mode(view_size)
    global clock
    clock = pygame.time.Clock()
    global running
    running = True
    global dT
    dT = 0.03
    global space
    space = Space()
    space.gravity = (0.0, 0.0)
    global life_list
    life_list = []
    global wall_list
    wall_list = []

def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global running
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pygame.image.save(screen, "contact_and_no_flipy.png")

def draw_life_collisions(arbiter, space, data) -> bool:
    for c in arbiter.contact_point_set.points:
        r = max(3, abs(c.distance * 5))
        r = int(r)
        p = tuple(map(int, c.point_a))
        gfxdraw.filled_circle(screen, p[0], flipy(p[1]), 6, Color("red"))
        print(f'collision: {p}')
    return True

def draw_edge_collisions(arbiter, space, data) -> bool:
    for c in arbiter.contact_point_set.points:
        p = tuple(map(int, c.point_a))
        gfxdraw.filled_circle(screen, p[0], flipy(p[1]), 6, Color("orange"))
        print(f'edge collision: {p}')
    return True

def add_life() -> tuple[Body, Shape, Life]:
    """ function with add single life to simulated world """
    size = randint(3, 10)
    life = Life(screen=screen, world_size=Vec2d(900, 600), size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    body, shape = life.get_body_and_shape()
    space.add(body, shape)
    return (body, shape, life)

def add_wall(point0: tuple, point1: tuple, thickness: float) -> tuple[Body, Shape, Wall]:
    """ function with add single wall to simulated world """
    wall = Wall(screen, point0, point1, thickness, Color('gray'), Color('gray'))
    body, shape = wall.get_body_and_shape()
    space.add(body, shape)
    return (body, shape, wall)

def main(world: tuple=(900, 600), view: tuple=(900, 600)):
    init(view)
    edges = [(5, 5), (895, 5), (895, 595), (5, 595), (5, 5)]
    
    for e in range(4):
        p1 = edges[e]
        p2 = edges[e+1]
        _, _, wall = add_wall(p1, p2, 5)
        wall_list.append(wall)

    for _ in range(20):
        _, _, life = add_life()
        life_list.append(life)


    life_collisions = space.add_collision_handler(1, 1)
    # life_collisions.data["surface"] = screen
    life_collisions.begin = draw_life_collisions

    edge_collisions = space.add_collision_handler(1, 2)
    #edge_collisions.data["surface"] = screen
    edge_collisions.begin = draw_edge_collisions

    while running:
        events()
        screen.fill(Color("black"))
        for life in life_list:
            life.update(dT)
            life.draw()

        for wall in wall_list:
            wall.draw()

        dt = 1.0 / 10.0
        for x in range(1):
            space.step(dt)
        pygame.display.flip()
        clock.tick(10)
        pygame.display.set_caption("NATURE v0.0.1      [fps: " + str(round(clock.get_fps(), 1)) + "]")


if __name__ == "__main__":
    sys.exit(main((900, 600), (900, 600)))