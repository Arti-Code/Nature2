import sys
from math import degrees
from random import randint
import pygame
from pygame import Color, Surface
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.life import Life, Detector
from lib.wall import Wall
from lib.math2 import set_world, world


life_list = []
wall_list = []
red_detection = []

world = (1100, 700)
flags = pygame.DOUBLEBUF | pygame.HWSURFACE
screen = pygame.display.set_mode(size=world, flags=flags, vsync=1)
FPS = 30
dt = 1/FPS
life_num = 5
running = True
clock = pygame.time.Clock()

def init(view_size: tuple):
    pygame.init()
    set_world(world)
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
    arbiter.shapes[0].body.position -= arbiter.normal*0.5
    arbiter.shapes[1].body.position += arbiter.normal*0.5
    target = arbiter.shapes[1].body
    target.color0 = Color('red')
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
    size = randint(7, 10)
    life = Life(screen=screen, space=space, world_size=world, size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    return life

def add_wall(point0: tuple, point1: tuple, thickness: float) -> Wall:
    wall = Wall(screen, space, point0, point1, thickness, Color('gray'), Color('gray'))
    #space.add(wall.shape, wall.body)
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

def physics_step(step_num: int, dt: float):
    for _ in range(1):
        space.step(dt)

def clock_step():
    global dt
    pygame.display.flip()
    dt = clock.tick(FPS)
    pygame.display.set_caption("NATURE v0.0.2      [fps: " + str(round(clock.get_fps(), 1)) + "]")

def main():
    init(world)
    create_enviro(world)
    #dt = 1.0 / FPS
    while running:
        events()
        update(dt)
        draw()
        #space.debug_draw(options)
        red_detection.clear()
        physics_step(1, dt)
        clock_step()
        

if __name__ == "__main__":
    sys.exit(main())