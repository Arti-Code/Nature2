import os
import sys
from math import degrees, hypot
from random import randint, random
import pygame
import pygame as pg
from pygame import Color, Surface
from pygame.constants import K_n
from pygame.font import Font, match_font 
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.life import Life, Creature, Plant
from lib.wall import Wall
from lib.sensor import Sensor
from lib.math2 import set_world, world, flipy
from lib.config import *
from lib.manager import Manager
#from lib.test import Test

global project
project = 'Nature'
creature_list = []
plant_list = []
wall_list = []
red_detection = []
global space
space = Space()
flags = pygame.DOUBLEBUF | pygame.HWSURFACE
screen = pygame.display.set_mode(size=WORLD, flags=flags, vsync=1)
FPS = 30
dt = 1/FPS
running = True
clock = pygame.time.Clock()
white = (255, 255, 255, 75)
red = (255, 0, 0, 75)
darkblue = (0, 0, 10, 255)
manager = Manager(screen=screen)
sel_idx = 0
show_network = False


def init(view_size: tuple):
    pygame.init()
    set_world(WORLD)
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
    global selected
    global sel_idx
    global running
    global show_network
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_LEFT:
                if sel_idx > 0 and sel_idx <= len(creature_list):
                    sel_idx -= 1
                    selected = creature_list[sel_idx]
                else:
                    sel_idx = 0
                    selected = creature_list[sel_idx]
            if event.key == pygame.K_RIGHT:
                if sel_idx >= 0 and sel_idx < (len(creature_list)-1):
                    sel_idx += 1
                    selected = creature_list[sel_idx]
            if event.key == pygame.K_n:
                show_network = not show_network
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

    creature_plant_collisions = space.add_collision_handler(2, 6)
    creature_plant_collisions.pre_solve = process_creature_plant_collisions

    edge_collisions = space.add_collision_handler(2, 8)
    edge_collisions.pre_solve = draw_edge_collisions

    detection = space.add_collision_handler(4, 2)
    detection.pre_solve = detect_creature

    detection_end = space.add_collision_handler(4, 2)
    detection_end.separate = detect_creature_end

    plant_detection = space.add_collision_handler(4, 6)
    plant_detection.pre_solve = detect_plant

    plant_detection_end = space.add_collision_handler(4, 6)
    plant_detection_end.separate = detect_plant_end

def process_creature_plant_collisions(arbiter, space, data):
    arbiter.shapes[0].body.position -= arbiter.normal*0.5
    arbiter.shapes[1].body.position += arbiter.normal*0.2
    #if arbiter.normal.angle <= 0.5 and arbiter.normal.angle >= -0.5:
    hunter = arbiter.shapes[0].body
    target = arbiter.shapes[1].body
    target.color0 = Color('red')
    #if isinstance(hunter, Creature) and isinstance(target, Plant):
    target.energy = target.energy - EAT
    if target.energy > 0:
        hunter.eat(EAT*20)
    return True

def draw_creature_collisions(arbiter, space, data):
    global dt
    arbiter.shapes[0].body.position -= arbiter.normal*0.5
    arbiter.shapes[1].body.position += arbiter.normal*0.5
    #if arbiter.normal.angle <= 0.5 and arbiter.normal.angle >= -0.5:
    size0 = arbiter.shapes[0].radius
    size1 = arbiter.shapes[1].radius
    if (size0+randint(0, 6)) > (size1+randint(0, 6)):
        arbiter.shapes[1].body.energy -= HIT/dt
        arbiter.shapes[1].body.color0=Color('red')
    return True

def draw_edge_collisions(arbiter, space, data):
    #arbiter.shapes[0].body.angle += arbiter.normal.angle
    arbiter.shapes[0].body.position -= arbiter.normal * 1.5
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

def detect_plant(arbiter, space, data):
    creature = arbiter.shapes[0].body
    plant = arbiter.shapes[1].body
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color('green'))
            pos0 = creature.position
            dist = pos0.get_distance(plant.position)
            sensor.send_data2(detect=True, distance=dist)
            break
    return True

def detect_plant_end(arbiter, space, data):
    return True

def detect_creature_end(arbiter, space, data):
    return True

def add_creature(world: tuple) -> Creature:
    size = randint(CREATURE_MIN_SIZE, CREATURE_MAX_SIZE)
    creature = Creature(screen=screen, space=space, collision_tag=2, world_size=world, size=size, color0=Color('blue'), color1=Color('turquoise'), color2=Color('orange'), color3=Color('red'), position=None)
    return creature

def add_plant(world: tuple):
    plant = Plant(screen=screen, space=space, collision_tag=6, world_size=world, size=3, color0=Color(LIME), color1=Color('darkgreen'), color3=Color(BROWN))
    return plant

def add_wall(point0: tuple, point1: tuple, thickness: float) -> Wall:
    wall = Wall(screen, space, point0, point1, thickness, Color('gray'), Color('gray'))
    #space.add(wall.shape, wall.body)
    return wall

def draw():
    screen.fill(Color(darkblue))
    for creature in creature_list:
        if creature == selected:
            creature.draw_detectors(screen=screen)
    for creature in creature_list:
        creature.draw(screen=screen, selected=selected)
    
    for plant in plant_list:
        plant.draw(screen=screen, selected=selected)
    
    for wall in wall_list:
        wall.draw(screen=screen)
    
    draw_network()
    draw_text()

def draw_text():
    font = Font(match_font('firacode'), 15)
    font.set_bold(True)
    if selected != None:
        info = font.render(f'energy: {round(selected.energy, 2)} | size: {round(selected.shape.radius)} | rep_time: {round(selected.reproduction_time)} | gen: {selected.generation}', True, Color('yellowgreen'))
        screen.blit(info, (411, 10), )
    count = font.render(f'creatures: {len(creature_list)} | plants: {len(plant_list)}', True, Color('yellow'))
    screen.blit(count, (10, 10), )

def draw_network():
    global show_network
    global selected
    if show_network:
        if isinstance(selected, Creature):
            manager.DrawNet(selected.neuro)

def update(dt: float):
    for creature in creature_list:
        if creature.energy <= 0:
            creature.kill(space)
            creature_list.remove(creature)
    update_creatures(dt)
    update_plants(dt)
    
def update_creatures(dt: float):
    temp_list = []
    for creature in creature_list:
        creature.get_input()
        creature.analize()
    for creature in creature_list:
        creature.move(dt)
    for creature in creature_list:
        creature.update(screen=screen, space=space, dt=dt)
        if creature.check_reproduction(dt):
            s, p, n, g = creature.reproduce(screen=screen, space=space)
            new_creature = Creature(screen=screen, space=space, collision_tag=2, world_size=WORLD, size=s, color0=Color('blue'), color1=Color('turquoise'), color2=Color('orange'), color3=Color('red'), position=p, generation=g+1)
            new_creature.neuro = n
            new_creature.neuro.Mutate()
            temp_list.append(new_creature)
    if random() <= CREATURE_MULTIPLY:
        creature = add_creature(world)
        creature_list.append(creature)
    for new_one in temp_list:
        creature_list.append(new_one)
    temp_list = []

def update_plants(dt: float):
    for plant in plant_list:
        if plant.life_time_calc(dt):
            plant.kill(space)
            plant_list.remove(plant)
    for plant in plant_list:
        if plant.energy <= 0:
            plant.kill(space)
            plant_list.remove(plant)
        else:
            plant.update(dt)
    if random() <= PLANT_MULTIPLY:
        plant = add_plant(WORLD)
        plant_list.append(plant)

def physics_step(step_num: int, dt: float):
    for _ in range(1):
        space.step(dt)

def clock_step():
    global dt
    pygame.display.flip()
    dt = clock.tick(FPS)
    pygame.display.set_caption(f"NATURE v0.1.0 [fps: {round(clock.get_fps())} | dT: {round(dt)}ms]")

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
    init(WORLD)
    create_enviro(WORLD)
    set_icon('planet05.png')
    #test = Test()
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