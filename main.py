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
    global dt
    dt = 0.03
    global space
    space = Space()
    space.gravity = (0.0, 0.0)
    space.damping = 0.1
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

def draw_life_collisions(arbiter, space, data):
    #for c in arbiter.contact_point_set.points:
    #    r = max(3, abs(c.distance * 5))
    #    r = int(r)
    #    p = tuple(map(int, c.point_a))
    #    gfxdraw.filled_circle(screen, p[0], flipy(p[1]), 6, Color("red"))
    #print(f'collision!')
    return True

def draw_edge_collisions(arbiter, space, data):
    #for c in arbiter.contact_point_set.points:
    #    p = tuple(map(int, c.point_a))
    #    gfxdraw.filled_circle(screen, p[0], flipy(p[1]), 6, Color("orange"))
    #print(f'edge collision!')
    return True

def add_life(world_size: tuple) -> tuple[Body, Shape, Life]:
    """ function with add single life to simulated world """
    size = randint(3, 10)
    life = Life(screen=screen, world_size=Vec2d(world_size[0], world_size[1]), size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    body, shape = life.get_body_and_shape()
    space.add(body, shape)
    return (body, shape, life)

def add_wall(point0: tuple, point1: tuple, thickness: float) -> tuple[Body, Shape, Wall]:
    """ function with add single wall to simulated world """
    wall = Wall(screen, point0, point1, thickness, Color('gray'), Color('gray'))
    body, shape = wall.get_body_and_shape()
    space.add(body, shape)
    return (body, shape, wall)

def draw():
    screen.fill(Color("black"))
    for life in life_list:
        life.draw()
    for wall in wall_list:
        wall.draw()

def update(dt: float):
    for life in life_list:
        life.update(dt)

def main(world: tuple=(900, 600), view: tuple=(900, 600)):
    init(view)
    edges = [(5, 5), (world[0]-5, 5), (world[0]-5, world[1]-5), (5, world[1]-5), (5, 5)]
    
    for e in range(4):
        p1 = edges[e]
        p2 = edges[e+1]
        _, _, wall = add_wall(p1, p2, 5)
        wall_list.append(wall)

    for _ in range(100):
        _, _, life = add_life(world)
        life_list.append(life)


    life_collisions = space.add_collision_handler(1, 1)
    # life_collisions.data["surface"] = screen
    life_collisions.begin = draw_life_collisions

    #edge_collisions = space.add_collision_handler(1, 2)
    #edge_collisions.data["surface"] = screen
    #edge_collisions.begin = draw_edge_collisions
    dt = 1.0 / 30.0
    while running:
        events()
        update(dt)
        draw()
        for x in range(1):
            space.step(dt)
        pygame.display.flip()
        dt = clock.tick(30)
        pygame.display.set_caption("NATURE v0.0.1      [fps: " + str(round(clock.get_fps(), 1)) + "]")


if __name__ == "__main__":
    sys.exit(main((1200, 700), (1200, 700)))