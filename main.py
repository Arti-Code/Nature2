import os
import sys
from time import time
from math import degrees, hypot
from statistics import mean
from random import randint, random
from typing import Union
import pygame
import pygame as pg
from pygame import Color, Surface, image
from pygame.constants import K_n
from pygame.font import Font, match_font 
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.life import Life
from lib.creature import Creature
from lib.plant import Plant
from lib.wall import Wall
from lib.sensor import Sensor
from lib.math2 import set_world, world, flipy
from lib.config import *
from lib.manager import Manager
from lib.autoterrain import Terrain
from lib.collisions import process_creature_plant_collisions, process_edge_collisions, process_creatures_collisions, detect_creature, detect_plant, detect_plant_end, detect_creature_end, detect_obstacle, detect_obstacle_end

class Simulation():

    def __init__(self, view_size: tuple):
        self.times = []
        self.time_text = 1
        self.physics_single_times = []
        self.physics_avg_time = 1
        self.project_name = None
        self.creature_list = []
        self.plant_list = []
        self.wall_list = []
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode(size=view_size, flags=flags, vsync=1)
        self.space = Space()
        self.FPS = 30
        self.dt = 1/self.FPS
        self.running = True
        self.clock = pygame.time.Clock()
        self.sel_idx = 0
        self.show_network = False
        self.manager = Manager(screen=self.screen, enviro=self)

        pygame.init()
        #self.create_enviro(WORLD)
        self.space.gravity = (0.0, 0.0)
        self.set_collision_calls()
        pymunk.pygame_util.positive_y_is_up = True
        self.selected = None
        self.options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(self.options)
        self.time = 0
        self.cycles = 0

    def create_enviro(self, world: tuple=None):
        self.time = 0
        self.cycles = 0
        self.kill_all_creatures()
        self.kill_all_plants()
        self.wall_list = []
        edges = [(0, 0), (WORLD[0]-1, 0), (WORLD[0]-1, WORLD[1]-1), (0, WORLD[1]-1), (0, 0)]
        for e in range(4):
            p1 = edges[e]
            p2 = edges[e+1]
            wall = self.add_wall(p1, p2, 5)
            self.wall_list.append(wall)
        #self.terr_img = image.load('res/fonts/water3.png')
        #self.terr_img.convert_alpha()
        #terrain = Terrain(self.screen, self.space, 'water3.png', 8)

        for c in range(CREATURE_INIT_NUM):
            creature = self.add_creature(WORLD)
            self.creature_list.append(creature)

        for p in range(PLANT_INIT_NUM):
            plant = self.add_plant(WORLD)
            self.plant_list.append(plant)

    def create_empty_world(self, world: tuple):
        self.time = 0
        self.cycles = 0
        self.kill_all_creatures()
        self.kill_all_plants()
        self.wall_list = []
        edges = [(0, 0), (WORLD[0]-1, 0), (WORLD[0]-1, WORLD[1]-1), (0, WORLD[1]-1), (0, 0)]
        for e in range(4):
            p1 = edges[e]
            p2 = edges[e+1]
            wall = self.add_wall(p1, p2, 5)
            self.wall_list.append(wall)

    def events(self):
        for event in pygame.event.get():
            self.manager.user_event(event, 1/self.dt)
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.key_events(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.mouse_events(event)

    def key_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        if event.key == pygame.K_LEFT:
            if self.creature_list != []:
                if self.sel_idx > 0 and self.sel_idx <= len(self.creature_list):
                    self.sel_idx -= 1
                    self.selected = self.creature_list[self.sel_idx]
                else:
                    self.sel_idx = 0
                    self.selected = self.creature_list[self.sel_idx]
        if event.key == pygame.K_RIGHT:
            if self.creature_list != []:
                if self.sel_idx >= 0 and self.sel_idx < (len(self.creature_list)-1):
                    self.sel_idx += 1
                    self.selected = self.creature_list[self.sel_idx]
        if event.key == pygame.K_n:
            self.show_network = not self.show_network

    def mouse_events(self, event):
        self.selected = None
        mouseX, mouseY = pg.mouse.get_pos()
        self.selected = self.find_creature(mouseX, flipy(mouseY))
        if self.selected == None:
            self.selected = self.find_plant(mouseX, flipy(mouseY))

    def find_plant(self, x: float, y: float) -> Union[Plant, None]:
        for plant in self.plant_list:
            if hypot(plant.position.x-x, plant.position.y-y) <= plant.shape.radius:
                return plant
        return None

    def find_creature(self, x: float, y: float) -> Union[Creature, None]:
        for creature in self.creature_list:
            if hypot(creature.position.x-x, creature.position.y-y) <= creature.shape.radius:
                return creature
        return None

    def set_collision_calls(self):
        # 2: body | 8: wall | 4: sensor | 6: plant
        creature_collisions = self.space.add_collision_handler(2, 2)
        creature_collisions.pre_solve = process_creatures_collisions
        creature_collisions.data['dt'] = self.dt

        creature_plant_collisions = self.space.add_collision_handler(2, 6)
        creature_plant_collisions.pre_solve = process_creature_plant_collisions
        creature_plant_collisions.data['dt'] = self.dt

        edge_collisions = self.space.add_collision_handler(2, 8)
        edge_collisions.pre_solve = process_edge_collisions

        detection = self.space.add_collision_handler(4, 2)
        detection.pre_solve = detect_creature

        detection_end = self.space.add_collision_handler(4, 2)
        detection_end.separate = detect_creature_end

        plant_detection = self.space.add_collision_handler(4, 6)
        plant_detection.pre_solve = detect_plant

        plant_detection_end = self.space.add_collision_handler(4, 6)
        plant_detection_end.separate = detect_plant_end

        obstacle_detection = self.space.add_collision_handler(4, 8)
        obstacle_detection.pre_solve = detect_obstacle

        obstacle_detection_end = self.space.add_collision_handler(4, 8)
        obstacle_detection_end.separate = detect_obstacle_end

    def add_creature(self, world: tuple) -> Creature:
        size = randint(CREATURE_MIN_SIZE, CREATURE_MAX_SIZE)
        creature = Creature(screen=self.screen, space=self.space, sim=self, collision_tag=2, world_size=WORLD, size=size, color0=Color('blue'), color1=Color('skyblue'), color2=Color('orange'), color3=Color('red'))
        return creature

    def add_saved_creature(self, size: int, color0: Color, color1: Color, color2: Color, color3: Color, position: tuple, generation: int, network_json: any):
        creature = Creature(screen=self.screen, space=self.space, sim=self, collision_tag=2, world_size=WORLD, size=size, color0=color0, color1=color1, color2=color2, color3=color3, position=position, generation=generation, network=network_json)
        creature.generation = generation
        self.creature_list.append(creature)

    def add_plant(self, world: tuple) -> Plant:
        plant = Plant(screen=self.screen, space=self.space, sim=self, collision_tag=6, world_size=world, size=3, color0=Color(LIME), color1=Color('darkgreen'), color3=Color(BROWN))
        return plant

    def add_wall(self, point0: tuple, point1: tuple, thickness: float) -> Wall:
        wall = Wall(self.screen, self.space, point0, point1, thickness, Color('gray'), Color('gray'))
        #space.add(wall.shape, wall.body)
        return wall

    def draw(self):
        self.screen.fill(Color('black'))
        #self.screen.blit(self.terr_img, (0, 0))
        for creature in self.creature_list:
            if creature == self.selected:
                creature.draw_detectors(screen=self.screen)
        for creature in self.creature_list:
            creature.draw(screen=self.screen, selected=self.selected)

        for plant in self.plant_list:
            plant.draw(screen=self.screen, selected=self.selected)

        for wall in self.wall_list:
            wall.draw(screen=self.screen)

        self.draw_network()
        self.draw_text()
        self.manager.draw_gui(screen=self.screen)

    def draw_text(self):
        font = Font(match_font('firacode'), FONT_SIZE)
        font.set_bold(True)
        if self.selected != None:
            info = font.render(f'energy: {round(self.selected.energy, 2)} | size: {round(self.selected.shape.radius)} | rep_time: {round(self.selected.reproduction_time)} | gen: {self.selected.generation}', True, Color('yellowgreen'))
            self.screen.blit(info, (SCREEN[0]/2-150, SCREEN[1]-25), )
        count = font.render(f'creatures: {len(self.creature_list)} | plants: {len(self.plant_list)} | neuro time: {round(self.time_text, 4)}s | physx time: {round(self.physics_avg_time , 4)}s', True, Color('yellow'))
        self.screen.blit(count, (20, SCREEN[1]-25), )

    def draw_network(self):
        if self.show_network:
            if isinstance(self.selected, Creature):
                self.manager.draw_net(self.selected.neuro)

    def calc_time(self):
        self.time += 0.1/self.dt
        if self.time > 1000:
            self.cycles += 1
            self.time = self.time%1000

    def get_time(self, digits: int=0):
        t = self.cycles*1000 + round(self.time, digits)
        return t

    def kill_all_creatures(self):
        for creature in self.creature_list:
            creature.kill(self.space)
        self.creature_list = []

    def kill_all_plants(self):
        for plant in self.plant_list:
            plant.kill(self.space)
        self.plant_list = []

    def update(self):
        self.calc_time()
        for creature in self.creature_list:
            if creature.energy <= 0:
                creature.kill(self.space)
                self.creature_list.remove(creature)
        self.update_creatures(self.dt)
        self.update_plants(self.dt)
        self.manager.update_gui(self.dt/1000)

    def update_creatures(self, dt: float):
        temp_list = []
        neuro_time = time()
        for creature in self.creature_list:
            #creature.get_input()
            creature.analize()
        neuro_time = time()-neuro_time
        self.times.append(neuro_time)
        if len(self.times) >= 150:
            self.time_text = mean(self.times)
            self.times = []
        for creature in self.creature_list:
            creature.move(dt)
        for creature in self.creature_list:
            creature.update(screen=self.screen, space=self.space, dt=dt)
            if creature.check_reproduction(dt):
                for _ in range(3):
                    s, p, n, g = creature.reproduce(screen=self.screen, space=self.space)
                    new_creature = Creature(screen=self.screen, space=self.space, sim=self, collision_tag=2, world_size=WORLD, size=s, color0=Color('blue'), color1=Color('turquoise'), color2=Color('orange'), color3=Color('red'), position=p, generation=g)
                    new_creature.neuro = n
                    new_creature.neuro.Mutate()
                    temp_list.append(new_creature)
        if random() <= CREATURE_MULTIPLY:
            creature = self.add_creature(world)
            self.creature_list.append(creature)
        for new_one in temp_list:
            self.creature_list.append(new_one)
        temp_list = []

    def update_plants(self, dt: float):
        for plant in self.plant_list:
            if plant.life_time_calc(dt):
                plant.kill(self.space)
                self.plant_list.remove(plant)
        for plant in self.plant_list:
            if plant.energy <= 0:
                plant.kill(self.space)
                self.plant_list.remove(plant)
            else:
                plant.update(dt)
        if random() <= PLANT_MULTIPLY:
            plant = self.add_plant(WORLD)
            self.plant_list.append(plant)

    def physics_step(self, step_num: int, dt: float):
        for _ in range(1):
            self.space.step(dt)

    def clock_step(self):
        pygame.display.flip()
        self.dt = self.clock.tick(self.FPS)
        pygame.display.set_caption(f"{TITLE} [fps: {round(self.clock.get_fps())} | dT: {round(self.dt)}ms]")

    def main(self):
        set_win_pos(20, 20)
        #self.init(WORLD)
        self.create_enviro(WORLD)
        set_icon('res/images/planet05.png')
        #test = Test()
        while self.running:
            self.events()
            self.update()
            self.draw()
            #self.space.debug_draw(self.options)
            physics_time = time()
            self.physics_step(1, self.dt)
            physics_time = time()-physics_time
            self.physics_single_times.append(physics_time)
            if len(self.physics_single_times) >= 150:
                self.physics_avg_time = mean(self.physics_single_times)
                self.physics_single_times = []
            self.clock_step()
        
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

if __name__ == "__main__":
    set_world(WORLD)
    sim = Simulation(WORLD)
    sys.exit(sim.main())