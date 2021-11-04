import os
import sys
from time import time
from math import degrees, hypot, sin, cos, pi as PI, floor, ceil
from collections import deque
from lib.math2 import clamp
from statistics import mean
from random import randint, random, choice
from typing import Union
import pygame
from pygame import Color, Surface, image
from pygame.constants import *
from pygame.math import Vector2
from pygame.time import Clock
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pymunk.pygame_util
from lib.creature import Creature
from lib.plant import Plant
from lib.wall import Wall
from lib.math2 import set_world, world, flipy
from lib.config import cfg, TITLE, SUBTITLE
from lib.manager import Manager
from lib.rock import Rock
from lib.collisions import *
from lib.meat import Meat
from lib.utils import log_to_file
from lib.camera import Camera
from lib.statistics import Statistics
from lib.terrain import Terrain, Terrain2

class Simulation():

    def __init__(self):
        self.neuro_single_times = []
        self.neuro_avg_time = 1
        self.physics_single_times = []
        self.physics_avg_time = 1
        self.project_name = None
        self.creature_list = []
        self.plant_list = []
        self.wall_list = []
        self.meat_list = []
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode(
            size=cfg.SCREEN, flags=flags, vsync=1)
        self.space = Space()
        self.FPS = 30
        self.dt = 1/self.FPS
        self.running = True
        self.clock = Clock()
        self.sel_idx = 0
        self.show_network = False
        self.manager = Manager(screen=self.screen, enviro=self)

        pygame.init()
        self.space.gravity = (0.0, 0.0)
        self.set_collision_calls()
        pymunk.pygame_util.positive_y_is_up = True
        self.selected = None
        self.options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(self.options)
        self.time = 0
        self.cycles = 0
        self.draw_debug: bool=False
        self.ranking1 = []
        self.ranking2 = []
        self.last_save_time = 0
        self.herbivores = 0
        self.carnivores = 0
        self.camera = Camera(Vector2(int(cfg.SCREEN[0]/2), int(cfg.SCREEN[1]/2)), Vector2(cfg.SCREEN[0], cfg.SCREEN[1]))
        self.creatures_on_screen = deque(range(30))
        self.plants_on_screen = deque(range(30))
        self.meats_on_screen = deque(range(30))
        self.rocks_on_screen = deque(range(30))
        self.statistics = Statistics()
        self.statistics.add_collection('populations', ['plants', 'herbivores', 'carnivores'])
        self.populations = {'period': 0, 'plants': [], 'herbivores': [], 'carnivores': []}
        self.terrain = Terrain((cfg.WORLD[0], cfg.WORLD[0]), 10, 0.15, (4, 8))
        #self.terrain.generate(self.space, cfg.WORLD, 1)  #
        self.terrain_surf = self.terrain.draw_tiles()
        self.terrain_surf.set_alpha(255)
        self.map_time = 0.0

    def create_rock(self, vert_num: int, size: int, position: Vec2d):
        ang_step = (2*PI)/vert_num
        vertices = []
        for v in range(vert_num):
            vert_ang = v*ang_step + (random()*2-1)*ang_step*0.4
            x = sin(vert_ang)*size + (random()*2-1)*size*0.4
            y = cos(vert_ang)*size + (random()*2-1)*size*0.4
            vertices.append(Vec2d(x, y)+position)
        rock = Rock(self.screen, self.space, vertices, 3, Color('grey40'), Color('grey'))
        self.wall_list.append(rock)
        
    def create_enviro(self):
        self.time = 0
        self.cycles = 0
        self.kill_all_creatures()
        self.kill_all_plants()
        self.kill_things()
        edges = [(0, 0), (cfg.WORLD[0]-1, 0), (cfg.WORLD[0]-1, cfg.WORLD[1]-1), (0, cfg.WORLD[1]-1), (0, 0)]
        for e in range(4):
            p1 = edges[e]
            p2 = edges[e+1]
            wall = self.add_wall(p1, p2, 5)
            self.wall_list.append(wall)
        #self.terr_img = image.load('res/fonts/water3.png')
        # self.terr_img.convert_alpha()
        #terrain = Terrain(self.screen, self.space, 'water3.png', 8)
        self.create_rocks(cfg.ROCK_NUM)

        for c in range(cfg.CREATURE_INIT_NUM):
            creature = self.add_creature()
            self.creature_list.append(creature)
        self.create_plants(cfg.PLANT_INIT_NUM)
    
    def create_borders(self):
        edges = [(0, 0), (cfg.WORLD[0]-1, 0), (cfg.WORLD[0]-1, cfg.WORLD[1]-1), (0, cfg.WORLD[1]-1), (0, 0)]
        for e in range(4):
            p1 = edges[e]
            p2 = edges[e+1]
            wall = self.add_wall(p1, p2, 8)
            self.wall_list.append(wall)

    def create_rocks(self, rock_num: int):
        for _r in range(rock_num):
            self.create_rock(5, 110, random_position(cfg.WORLD))

    def create_plants(self, plant_num: int):
        for _p in range(plant_num):
            plant = self.add_plant(True)
            self.plant_list.append(plant)

    def create_empty_world(self):
        self.time = 0
        self.cycles = 0
        self.kill_all_creatures()
        self.kill_all_plants()
        self.kill_things()

    def add_to_ranking(self, creature: Creature):
        if creature.food >= 6:
            ranking = self.ranking2
        else:
            ranking = self.ranking1
        #ranking = self.ranking1
        ranking.sort(key=sort_by_fitness, reverse=True)
        for rank in reversed(ranking):
            if rank['name'] == creature.name:
                if creature.fitness >= rank['fitness']:
                    ranking.remove(rank)
                    ranking.append(creature.get_genome())
                    ranking.sort(key=sort_by_fitness, reverse=True)
                    return
                else:
                    return
        if len(ranking) <= cfg.RANK_SIZE:
            cr = creature.get_genome()
            cr['fitness'] = round(cr['fitness'])
            ranking.append(cr)
        else:
            for r in ranking:
                if r['fitness'] <= creature.fitness:
                    ranking.remove(r)
                    cr = creature.get_genome()
                    cr['fitness'] = round(cr['fitness'])
                    ranking.append(cr)
        ranking.sort(key=sort_by_fitness, reverse=True)
        if len(ranking) > cfg.RANK_SIZE:
            ranking.pop(len(ranking)-1)

    def events(self):
        for event in pygame.event.get():
            self.manager.user_event(event, 1*self.dt)
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.key_events(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.mouse_events(event)

    def key_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        if event.key == pygame.K_KP_8:
            self.camera.update(Vector2(0, -50))
        if event.key == pygame.K_KP_2:
            self.camera.update(Vector2(0, 50))
        if event.key == pygame.K_KP_4:
            self.camera.update(Vector2(-50, 0))
        if event.key == pygame.K_KP_6:
            self.camera.update(Vector2(50, 0))
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
        if event.key == pygame.K_d:
            self.draw_debug = not self.draw_debug

    def mouse_events(self, event):
        self.selected = None
        mouseX, mouseY = pygame.mouse.get_pos()
        rel_mouse = self.camera.rev_pos(Vector2(mouseX, mouseY))
        #print(f'mouse: {mouseX}|{mouseY} -> {rel_mouse.x}|{rel_mouse.y}')
        self.selected = self.find_creature(rel_mouse.x, flipy(rel_mouse.y))
        if self.selected == None:
            self.selected = self.find_plant(rel_mouse.x, flipy(rel_mouse.y))
        if self.selected == None:
            self.selected = self.find_meat(rel_mouse.x, flipy(rel_mouse.y))

    def find_plant(self, x: float, y: float) -> Union[Plant, None]:
        for plant in self.plant_list:
            if hypot(plant.position.x-x, plant.position.y-y) <= plant.shape.radius:
                return plant
        return None

    def find_meat(self, x: float, y: float) -> Union[Meat, None]:
        for meat in self.meat_list:
            if hypot(meat.position.x-x, meat.position.y-y) <= meat.shape.radius:
                return meat
        return None

    def find_creature(self, x: float, y: float) -> Union[Creature, None]:
        for creature in self.creature_list:
            if hypot(creature.position.x-x, creature.position.y-y) <= creature.shape.radius:
                return creature
        return None

    def set_collision_calls(self):
        #* 2: body | 8: wall | 4: sensor | 6: plant | 12: new_plant | 16: eye | 10: meat
        creature_collisions = self.space.add_collision_handler(2, 2)
        creature_collisions.pre_solve = process_creatures_collisions
        creature_collisions.data['dt'] = self.dt

        creature_plant_collisions = self.space.add_collision_handler(2, 6)
        creature_plant_collisions.pre_solve = process_creature_plant_collisions
        creature_plant_collisions.data['dt'] = self.dt

        creature_meat_collisions = self.space.add_collision_handler(2, 10)
        creature_meat_collisions.pre_solve = process_creature_meat_collisions
        creature_meat_collisions.data['dt'] = self.dt

        creature_detection = self.space.add_collision_handler(4, 2)
        creature_detection.pre_solve = detect_creature

        creature_detection_end = self.space.add_collision_handler(4, 2)
        creature_detection_end.separate = detect_creature_end

        plant_detection = self.space.add_collision_handler(4, 6)
        plant_detection.pre_solve = detect_plant

        plant_detection_end = self.space.add_collision_handler(4, 6)
        plant_detection_end.separate = detect_plant_end

        meat_detection = self.space.add_collision_handler(4, 10)
        meat_detection.pre_solve = detect_meat

        meat_detection_end = self.space.add_collision_handler(4, 10)
        meat_detection_end.separate = detect_meat_end

    def add_creature(self, genome: dict=None, pos: Vec2d=None) -> Creature:
        creature: Creature
        if pos is None:
            pos = random_position(cfg.WORLD)
        x = clamp(pos[0], 0, cfg.WORLD[0])
        y = clamp(pos[1], 0, cfg.WORLD[1])
        cpos = Vec2d(x, y)
        if genome is None:
            creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=cpos, color0=Color('white'), color1=Color('skyblue'), color2=Color('blue'), color3=Color('red'))
        else:
            creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=cpos, genome=genome)
        return creature

    def add_saved_creature(self, genome: dict):
        creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=random_position(cfg.WORLD), genome=genome)
        self.creature_list.append(creature)

    def add_plant(self, mature: bool=False) -> Plant:
        if mature:
            size = cfg.PLANT_MAX_SIZE
        else:
            size = 3
        free_field = False
        while not free_field:
            x = randint(50, cfg.WORLD[0]-50)
            y = randint(50, cfg.WORLD[1]-50)
            pos = Vec2d(x, y)
            free_field = True
            for rock in self.wall_list:
                d =  rock.shape.point_query(pos).distance
                if d <= 0:
                    free_field = False
                    break
        plant = Plant(screen=self.screen, space=self.space, collision_tag=6, world_size=world,
                      size=size, color0=Color((127, 255, 0)), color1=Color('darkgreen'), color3=Color((110, 50, 9)), position=pos)
        return plant

    def add_wall(self, point0: tuple, point1: tuple, thickness: float) -> Wall:
        wall = Wall(self.screen, self.space, point0, point1,
                    thickness, Color('gray'), Color('navy'))
        return wall

    def draw(self):
        self.screen.fill(Color('black'))
        self.screen.blit(self.terrain_surf, (0, 0))
        screen_crs = 0
        screen_plants = 0
        screen_meats = 0
        screen_rocks = 0
        for creature in self.creature_list:
            if creature.draw(screen=self.screen, camera=self.camera, selected=self.selected):
                screen_crs += 1
            #creature.draw_detectors(screen=self.screen)
            name, x, y = creature.draw_name(camera=self.camera)
            self.manager.add_text2(name, x, y, Color('skyblue'))

        for plant in self.plant_list:
            if plant.draw(screen=self.screen, camera=self.camera, selected=self.selected):
                screen_plants += 1

        for wall in self.wall_list:
            if wall.draw(screen=self.screen, camera=self.camera):
                screen_rocks += 1

        for meat in self.meat_list:
            if meat.draw(screen=self.screen, camera=self.camera, selected=self.selected):
                screen_meats += 1

        self.creatures_on_screen.append(screen_crs)
        self.plants_on_screen.append(screen_plants)
        self.rocks_on_screen.append(screen_rocks)
        self.meats_on_screen.append(screen_meats)
        self.creatures_on_screen.popleft()
        self.plants_on_screen.popleft()
        self.rocks_on_screen.popleft()
        self.meats_on_screen.popleft()
        self.draw_network()
        #self.draw_text()
        self.write_text()
        self.manager.draw_gui(screen=self.screen)

    def draw_text(self):
        if self.selected != None:
            if isinstance(self.selected, Creature):
                self.manager.add_text2(f'energy: {round(self.selected.energy)} | life_time: {round(self.selected.life_time)} | run_time: {round(self.selected.run_time)} | size: {round(self.selected.shape.radius)} | rep_time: {round(self.selected.reproduction_time)} | gen: {self.selected.generation} | food: {self.selected.food} | fit: {round(self.selected.fitness)}', cfg.SCREEN[0]/2-150, cfg.SCREEN[1]-25, Color('yellowgreen'), False, False, True, False)
            elif isinstance(self.selected, Plant):
                self.manager.add_text2(f'energy: {round(self.selected.energy)} | size: {round(self.selected.shape.radius)} | time: {round(self.selected.life_time)}', cfg.SCREEN[0]/2-150, cfg.SCREEN[1]-25, Color('yellowgreen'), False, False, True, False)
            elif isinstance(self.selected, Meat):
                self.manager.add_text2(f'energy: {round(self.selected.energy)} | size: {round(self.selected.radius)} | time: {round(self.selected.time)}', cfg.SCREEN[0]/2-150, cfg.SCREEN[1]-25, Color('yellowgreen'), False, False, True, False)
            else:                
                self.manager.add_text2(f'no info', cfg.SCREEN[0]/2-150, cfg.SCREEN[1]-25, Color('yellowgreen'), False, False, True, False)
    
    def write_text(self):
        for txt, rect in self.manager.text_list:
            self.screen.blit(txt, rect)
        self.manager.text_list.clear()

    def draw_network(self):
        if self.show_network:
            if isinstance(self.selected, Creature):
                self.manager.draw_net(self.selected.neuro)

    def calc_time(self):
        self.time += self.dt*0.1
        if self.time > 6000:
            self.cycles += 1
            self.time = self.time % 6000

    def get_time(self, digits: int = None):
        return self.cycles*6000 + round(self.time, digits)

    def kill_all_creatures(self):
        for creature in self.creature_list:
            creature.kill(self.space)
        self.creature_list = []

    def kill_all_plants(self):
        for plant in self.plant_list:
            plant.kill(self.space)
        self.plant_list = []

    def kill_things(self):
        for wall in self.wall_list:
            wall.kill(self.space)
        self.wall_list = []

    def update(self):
        self.calc_time()
        self.update_creatures(self.dt)
        self.update_plants(self.dt)
        self.update_meat(self.dt)
        #self.update_statistics()
        self.update_terrain(self.dt)
        self.manager.update_gui(self.dt, self.ranking1, self.ranking2)

    def update_meat(self, dT: float):
        for meat in self.meat_list:
            meat.update(dT, self.selected)
            if meat.time <= 0 or meat.energy <= 0:
                meat.kill(self.space)
                self.meat_list.remove(meat)

    def update_creatures(self, dt: float):
        ### CHECK ENERGY ###
        for creature in self.creature_list:
            if creature.energy <= 0 or creature.water <= 0:
                self.add_to_ranking(creature)
                if not creature.on_water:
                    meat = Meat(screen=self.screen, space=self.space, position=creature.position, collision_tag=10, radius=creature.size, energy=creature.max_energy)
                    self.meat_list.append(meat)
                creature.kill(self.space)
                self.creature_list.remove(creature)

        ### ANALIZE ###
        neuro_time = time()
        for creature in self.creature_list:
            creature.analize()
        neuro_time = time()-neuro_time
        self.neuro_single_times.append(neuro_time)
        if len(self.neuro_single_times) >= 150:
            self.neuro_avg_time = mean(self.neuro_single_times)
            self.neuro_single_times = []

        ### MOVEMENT ###
        #for creature in self.creature_list:
        #    creature.move(dt)

        ### REPRODUCE ###
        temp_list = []
        for creature in self.creature_list:
            creature.update(dt=dt, selected=self.selected)
            if creature.check_reproduction(dt):
                for _ in range(cfg.CHILDS_NUM):
                    genome, position = creature.reproduce(screen=self.screen, space=self.space)
                    new_creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=position, genome=genome)
                    temp_list.append(new_creature)

        if random() <= cfg.CREATURE_MULTIPLY:
            creature = self.add_random_creature()
            self.creature_list.append(creature)

        for new_one in temp_list:
            self.creature_list.append(new_one)
        temp_list = []
        self.check_populatiom()

    def update_terrain(self, dt):
        self.map_time += dt
        if self.map_time < 1.0:
            return
        #self.terrain.update()
        for creature in self.creature_list:
            coord0 = creature.get_tile_coord()
            vec = creature.rotation_vector
            coord = ((creature.position+(vec*100))/10)
            creature.water_ahead = False
            water_detectors = creature.detect_water(self.screen)
            for detector in water_detectors:
                if self.terrain.is_water_tile(detector):
                    creature.water_ahead = True
                    break
            on_water_tile = self.terrain.is_water_tile(coord0)
            if on_water_tile[0]:
                creature.on_water = (True, on_water_tile[1])
                #creature.drink(dt)
            else:
                creature.on_water = (False, on_water_tile[1])
            #    a, b = sensor.get_points()
            #    sensor.detect_water(self.terrain.detect_water(sensor.get_rect(), a, b))
            #vec = creature.rotation_vector.int_tuple
            #coord0 = coord
            #coord1 = (coord0[0]+(vec[0]), coord0[1]-((vec[1])))
            #coords = [coord0, coord1]
            
            #if self.terrain.is_water_tile(coord1):
            #    creature.water_ahead = True
            #else:
            #    creature.water_ahead = False
        #    for coord in coords:   
        #        self.terrain.set_occupied(coord, True)
        #self.terrain_surf = self.terrain.draw_tiles()
        #self.terrain_surf.set_alpha(255)
        self.map_time = self.map_time-1.0

    def update_statistics(self):
        t = int(self.get_time()/cfg.STAT_PERIOD)
        if t > self.populations['period']:
            data = {
                'plants': round(mean(self.populations['plants'])), 
                'herbivores': round(mean(self.populations['herbivores'])), 
                'carnivores': round(mean(self.populations['carnivores']))
            }
            self.statistics.add_data('populations', data)
            self.populations = {'period': t, 'plants': [], 'herbivores': [], 'carnivores': []}
        else:
            self.populations['plants'].append(len(self.plant_list))
            self.populations['herbivores'].append(self.herbivores)
            self.populations['carnivores'].append(self.carnivores)

    def check_creature_types(self):
        self.herbivores = 0
        self.carnivores = 0
        for creature in self.creature_list:
            if creature.food < 6:
                self.herbivores += 1
            else:
                self.carnivores += 1

        if self.herbivores < cfg.MIN_HERBIVORES:
            if len(self.ranking1) > 0:
                genome = choice(self.ranking1)
                creature = self.add_creature(genome=genome)
                self.creature_list.append(creature)
        if self.carnivores < cfg.MIN_CARNIVORES:
            if len(self.ranking2) > 0:
                genome = choice(self.ranking2)
                creature = self.add_creature(genome=genome)
                self.creature_list.append(creature)
 
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
                plant.update(dt, self.selected)
        if random() <= cfg.PLANT_MULTIPLY:
            plant = self.add_plant(cfg.WORLD)
            self.plant_list.append(plant)

    def physics_step(self, dt: float):
        for _ in range(1):
            self.space.step(dt)

    def clock_step(self):
        pygame.display.flip()
        self.dt = self.clock.tick(self.FPS)/1000*cfg.TIME
        pygame.display.set_caption(
            f"{TITLE} [fps: {round(self.clock.get_fps())} | dT: {round(self.dt*1000)}ms]")

    def check_populatiom(self):
        if randint(0, 9) == 0:
            self.check_creature_types()

        if len(self.creature_list) < cfg.CREATURE_MIN_NUM:
            creature = self.add_random_creature()
            self.creature_list.append(creature)

    def add_random_creature(self) -> Creature:
        r = randint(0, 1)
        creature: Creature = None
        if r == 0 or len(self.ranking1) == 0 or len(self.ranking2) == 0:
            creature = self.add_creature()
        else:
            ranking = choice([self.ranking1, self.ranking2])
            rank_size = len(ranking)
            rnd = randint(0, rank_size-1)
            genome = ranking[rnd]
            ranking[rnd]['fitness'] *= cfg.RANK_DECAY
            creature = self.add_creature(genome)
        return creature

    def auto_save(self):
        if floor((self.cycles*6000+self.time)-self.last_save_time) >= cfg.AUTO_SAVE_TIME:
            self.manager.save_project()
            self.last_save_time = round((self.cycles*6000+self.time), 1)
    
    def main(self):
        set_win_pos(20, 20)
        # self.init(cfg.WORLD)
        self.create_enviro()
        set_icon('planet32.png')
        #test = Test()
        while self.running:
            self.auto_save()
            self.events()
            self.update()
            self.draw()
            if self.draw_debug:
                self.space.debug_draw(self.options)
            physics_time = time()
            self.physics_step(self.dt)
            physics_time = time()-physics_time
            self.physics_single_times.append(physics_time)
            if len(self.physics_single_times) >= 150:
                self.physics_avg_time = mean(self.physics_single_times)
                self.physics_single_times = []
            self.clock_step()


def set_win_pos(x: int = 20, y: int = 20):
    x_winpos = x
    y_winpos = y
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x_winpos, y_winpos)


def random_position(space: tuple) -> list:
    x = randint(0+20, space[0]-20)
    y = randint(0+20, space[1]-20)
    pos = [x, y]
    return pos


def set_icon(icon_name):
    icon = pygame.Surface((32, 32))
    icon.set_colorkey((0, 0, 0))
    rawicon = pygame.image.load(icon_name)
    for i in range(0, 32):
        for j in range(0, 32):
            icon.set_at((i, j), rawicon.get_at((i, j)))
    pygame.display.set_icon(icon)


def sort_by_fitness(creature):
    return creature['fitness']


if __name__ == "__main__":
    set_world(cfg.WORLD)
    sim = Simulation()
    sys.exit(sim.main())
