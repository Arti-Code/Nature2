""" DEVELOPMENT BRANCH """

import sys
from math import degrees
from random import randint
import pygame
from pygame import Color, Surface
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.life import Life, Detector
from lib.wall import Wall


life_list = []
wall_list = []
red_detection = []
dt = 0.03
space = Space()
screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)
FPS = 20
life_num = 5
running = True
clock = pygame.time.Clock()

def init(view_size: tuple):
    pygame.init()
    space.gravity = (0.0, 0.0)
    set_collision_calls()
    pymunk.pygame_util.positive_y_is_up = True
    global options
    options = pymunk.pygame_util.DrawOptions(screen)
    space.debug_draw(options)

def create_enviro(world: tuple):
    edges = [(5, 5), (world[0]-5, 5), (world[0]-5, world[1]-5), (5, world[1]-5), (5, 5)]
    for e in range(4):
        p1 = edges[e]
        p2 = edges[e+1]
        wall = add_wall(p1, p2, 5)
        wall_list.append(wall)

    for l in range(life_num):
        life = add_life(world)
        life_list.append(life)

def events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

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
    arbiter.shapes[0].body.angle += arbiter.normal.angle
    arbiter.shapes[0].body.position -= arbiter.normal * 10
    return True

def detect_life(arbiter, space, data):
    detector = arbiter.shapes[0]
    if detector in red_detection:
        return True
    else:
        red_detection.append(arbiter.shapes[0])
        return True

def detect_life_end(arbiter, space, data):
    detector = arbiter.shapes[0]
    black_list = []
    if detector in red_detection:
        black_list.append(detector)
    for detector in black_list:
        red_detection.remove(detector)

def add_life(world_size: tuple) -> Life:
    """ function with add single life to simulated world """
    size = randint(7, 10)
    life = Life(screen=screen,space=space, world_size=Vec2d(world_size[0], world_size[1]), size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    #space.add(life.body, life.shape, life.detectors[0].shape, life.detectors[1].shape, life.detectors[2].shape)
    return life

def add_wall(point0: tuple, point1: tuple, thickness: float) -> Wall:
    """ function with add single wall to simulated world """
    wall = Wall(screen, point0, point1, thickness, Color('gray'), Color('gray'))
    #space.add(wall, wall.shape)
    space.add(wall.shape, wall.body)
    return wall

def draw():
    screen.fill(Color("black"))
    for life in life_list:
        life.draw()
    for wall in wall_list:
        wall.draw()

def update(dt: float):
    for life in life_list:
        life.update(space, dt, red_detection)

def main(world: tuple=(600, 600), view: tuple=(600, 600)):
    init(view)
    create_enviro(world)
    dt = 1.0 / FPS
    while running:
        events()
        update(dt)
        screen.fill(Color("black"))
        draw()
        #space.debug_draw(options)
        red_detection.clear()
        for _ in range(1):
            space.step(dt)
        pygame.display.flip()
        dt = clock.tick(FPS)
        pygame.display.set_caption("NATURE v0.0.1      [fps: " + str(round(clock.get_fps(), 1)) + "]")
        

if __name__ == "__main__":
    #sys.exit(main(screen_size, screen_size))
    sys.exit(main((600, 600), (600, 600)))