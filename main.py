""" DEVELOPMENT BRANCH """

import sys
from math import degrees
from random import randint
import pygame
from pygame import Color, Surface
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
#import pymunk.pygame_util
from lib.life import Life
from lib.wall import Wall


life_list = []
wall_list = []
eyes = []
dt = 0.03
space = Space()
screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)
FPS = 30
life_num = 4

def init(view_size: tuple):
    pygame.init()
    global clock
    clock = pygame.time.Clock()
    global running
    running = True
    space.gravity = (0.0, 0.0)
    space.damping = 0.1
    set_collision_calls()

def create_enviro(world: tuple):
    edges = [(5, 5), (world[0]-5, 5), (world[0]-5, world[1]-5), (5, world[1]-5), (5, 5)]
    
    for e in range(4):
        p1 = edges[e]
        p2 = edges[e+1]
        _, _, wall = add_wall(p1, p2, 2)
        wall_list.append(wall)

    for _ in range(life_num):
        _, _, _, life = add_life(world)
        life_list.append(life)

def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pygame.image.save(screen, "contact_and_no_flipy.png")

def set_collision_calls():
    # 2: body | 8: wall | 4: sensor
    life_collisions = space.add_collision_handler(2, 2)
    life_collisions.pre_solve = draw_life_collisions

    edge_collisions = space.add_collision_handler(2, 8)
    edge_collisions.pre_solve = draw_edge_collisions

    detection = space.add_collision_handler(4, 2)
    detection.pre_solve = detect_life

    detection_end = space.add_collision_handler(4, 2)
    detection_end.separate = detect_life_end

def draw_life_collisions(arbiter, space, data):
    arbiter.shapes[0].body.position -= arbiter.normal
    arbiter.shapes[1].body.position += arbiter.normal
    return True

def draw_edge_collisions(arbiter, space, data):
    arbiter.shapes[0].body.position -= arbiter.normal
    return True

def detect_life(arbiter, space, data):
    detector = arbiter.shapes[0]
    if detector in eyes:
        return True
    else:
        eyes.append(arbiter.shapes[0])
        return True

def detect_life_end(arbiter, space, data):
    detector = arbiter.shapes[0]
    black_list = []
    if detector in eyes:
        black_list.append(detector)
    for detector in black_list:
        eyes.remove(detector)

def add_life(world_size: tuple) -> tuple[Body, Shape, Life]:
    """ function with add single life to simulated world """
    size = randint(8, 16)
    life = Life(screen=screen, world_size=Vec2d(world_size[0], world_size[1]), size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    body, shape, eye = life.get_body_and_shapes()
    space.add(body, shape, eye)
    return (body, shape, eye, life)

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
        life.update(dt, eyes)

def main(world: tuple=(900, 600), view: tuple=(900, 600)):
    init(view)
    create_enviro(world)
    dt = 1.0 / FPS
    while running:
        events()
        update(dt)
        draw()
        eyes.clear()
        for _ in range(1):
            space.step(dt)
        pygame.display.flip()
        dt = clock.tick(FPS)
        pygame.display.set_caption("NATURE v0.0.1      [fps: " + str(round(clock.get_fps(), 1)) + "]")
        

if __name__ == "__main__":
    sys.exit(main(screen_size, screen_size))
    #sys.exit(main((1200, 700), (1200, 700)))