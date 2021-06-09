import os
import sys
from math import degrees, hypot
from random import randint
import pygame
import pygame as pg
from pygame import Color, Surface
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.life import Life, Creature, Plant
from lib.wall import Wall
from lib.sensor import Sensor
from lib.math2 import set_world, world, flipy
from lib.config import *


creature_list = []
plant_list = []
wall_list = []
red_detection = []
space = Space()
world = (1000, 650)
flags = pygame.DOUBLEBUF | pygame.HWSURFACE
screen = pygame.display.set_mode(size=world, flags=flags, vsync=1)
FPS = 30
dt = 1/FPS
creature_num = 20
plant_num = 20
running = True
clock = pygame.time.Clock()
white = (255, 255, 255, 75)
red = (255, 0, 0, 75)
darkblue = (0, 0, 10, 255)


def init(view_size: tuple):
    pygame.init()
    set_world(world)
    space.gravity = (0.0, 0.0)
    set_collision_calls()
    pymunk.pygame_util.positive_y_is_up = True
    global selected
    selected = None
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

    for c in range(CREATURE_INIT_NUM):
        creature = add_creature(world)
        creature_list.append(creature)

    for p in range(PLANT_INIT_NUM):
        plant = add_plant(world)
        plant_list.append(plant)

def events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_events(event)

def mouse_events(event):
    global selected
    selected = None
    mouseX, mouseY = pg.mouse.get_pos()
    selected = FindCreature(mouseX, flipy(mouseY))
    if selected == None:
        selected = FindPlant(mouseX, flipy(mouseY))

def FindPlant(x, y):
    for plant in plant_list:
        if hypot(plant.position.x-x, plant.position.y-y) <= plant.shape.radius:
            return plant
    return None

def FindCreature(x, y):
    for creature in creature_list:
        if hypot(creature.position.x-x, creature.position.y-y) <= creature.shape.radius:
            return creature
    return None

def set_collision_calls():
    # 2: body | 8: wall | 4: sensor
    creature_collisions = space.add_collision_handler(2, 2)
    creature_collisions.pre_solve = draw_creature_collisions

    edge_collisions = space.add_collision_handler(2, 8)
    edge_collisions.pre_solve = draw_edge_collisions

    detection = space.add_collision_handler(4, 2)
    detection.pre_solve = detect_creature

    detection_end = space.add_collision_handler(4, 2)
    detection_end.separate = detect_creature_end

def draw_creature_collisions(arbiter, space, data):
    arbiter.shapes[0].body.position -= arbiter.normal*0.5
    arbiter.shapes[1].body.position += arbiter.normal*0.5
    target = arbiter.shapes[1].body
    target.color0 = Color('red')
    return True

def draw_edge_collisions(arbiter, space, data):
    arbiter.shapes[0].body.angle += arbiter.normal.angle
    arbiter.shapes[0].body.position -= arbiter.normal * 10
    return True

def detect_creature(arbiter, space, data):
    creature = arbiter.shapes[0].body
    enemy = arbiter.shapes[1].body
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color(red))
            pos0 = creature.position
            dist = pos0.get_distance(enemy.position)
            sensor.send_data(detect=True, distance=dist)
            break
    return True
    #if detector in red_detection:
    #    return True
    #else:
    #    red_detection.append(arbiter.shapes[0])
    #    return True

def detect_creature_end(arbiter, space, data):
    return True
    #detector = arbiter.shapes[0]
    #black_list = []
    #if detector in red_detection:
    #    black_list.append(detector)
    #for detector in black_list:
    #    red_detection.remove(detector)

def add_creature(world_size: tuple) -> Creature:
    size = randint(7, 10)
    creature = Creature(screen=screen, space=space, world_size=world, size=size, color0=Color('blue'), color1=Color('turquoise'), color2=Color('orange'))
    return creature

def add_plant(world_size: tuple):
    plant = Plant(screen=screen, space=space, world_size=world, size=10, color0=Color('yellowgreen'), color1=Color('green'))
    return plant


def add_wall(point0: tuple, point1: tuple, thickness: float) -> Wall:
    wall = Wall(screen, space, point0, point1, thickness, Color('gray'), Color('gray'))
    #space.add(wall.shape, wall.body)
    return wall

def draw():
    screen.fill(Color(darkblue))
    for creature in creature_list:
        creature.draw_detectors()
    for creature in creature_list:
        creature.draw(selected)
    
    for plant in plant_list:
        plant.draw(selected)
    
    for wall in wall_list:
        wall.draw()

def update(dt: float):
    for creature in creature_list:
        if creature.energy <= 0:
            creature_list.remove(creature)
    for creature in creature_list:
        creature.update(space, dt, red_detection)
    
    for plant in plant_list:
        plant.update(dt)

def physics_step(step_num: int, dt: float):
    for _ in range(1):
        space.step(dt)

def clock_step():
    global dt
    pygame.display.flip()
    dt = clock.tick(FPS)
    pygame.display.set_caption(f"NATURE [fps: {round(clock.get_fps())} | dT: {round(dt)}ms]")

def set_win_pos(x: int=20, y: int=20):
    x_winpos = x
    y_winpos = y
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x_winpos, y_winpos)

def set_icon(icon_name):
    icon = pg.Surface((32,32))
    icon.set_colorkey((0,0,0))
    rawicon = pg.image.load(icon_name)
    for i in range(0,32):
        for j in range(0,32):
            icon.set_at((i,j), rawicon.get_at((i,j)))
    pg.display.set_icon(icon)

def sort_by_fitness(creature):
    return creature['fitness']

def main():
    set_win_pos(20, 20)
    init(world)
    create_enviro(world)
    set_icon('planet05-32.png')
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