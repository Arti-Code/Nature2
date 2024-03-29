import os
import sys
from copy import copy, deepcopy
from collections import deque
from math import ceil, cos, floor, hypot
from math import pi as PI
from math import sin
from random import randint, random
from statistics import mean
from time import time
from typing import Union

import pygame
import pygame.draw as draw
import pymunk.pygame_util
from pygame import Color, image, Surface, Rect
from pygame.constants import *
from pygame.math import Vector2
from pygame.time import Clock
from pymunk import ShapeFilter, Space, Vec2d

from lib.config import TITLE, cfg
from lib.camera import Camera
from lib.collisions import *
from lib.creature import Creature
from lib.manager import Manager
from lib.math2 import flipy, set_world, world, clamp
from lib.meat import Meat
from lib.plant import Plant
from lib.rock import Rock
from lib.sim_stat import Statistics
from lib.wall import Wall
from lib.spike import Spike
#from lib.net_draw import draw_net, draw_net2
from perlin_noise import PerlinNoise

class Simulation():

    def __init__(self):
        self.scale = 1
        self.screen = pygame.display.set_mode(size=cfg.SCREEN, flags=0, vsync=1)
        self.space = Space()
        self.space.iterations = cfg.ITER
        self.sleep_time_treashold = 0.1
        self.clock = Clock()
        pygame.init()
        self.init_vars()
        self.manager = Manager(screen=self.screen, enviro=self)
        self.space.gravity = (0.0, 0.0)
        set_collision_calls(self.space, self.dt, self.creatures_num)
        pymunk.pygame_util.positive_y_is_up = False
        self.options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(self.options)
        self.draw_debug: bool=False
        self.draw_eng_bars: bool=True
        self.camera = Camera(Vector2(int(cfg.SCREEN[0]/2), int(cfg.SCREEN[1]/2)), Vector2(cfg.SCREEN[0], cfg.SCREEN[1]))
        self.statistics = Statistics()
        self.statistics.add_collection('populations', ['plants', 'herbivores', 'carnivores', 'all'])
        self.statistics.add_collection('creatures', ['size', 'speed', 'food', 'power', 'mutations', 'vision'])
        self.statistics.add_collection('neuros', ['nodes', 'links'])
        self.statistics.add_collection('fitness', ['points', 'lifetime'])
        self.update_time: float = 0.0
        self.draw_time: float = 0.0
        self.neuro_time: float = 0.0
        self.physics_time: float = 0.0
        self.net_timer: float=0.0
        self.net: Surface=None
        #self.grid: Surface = self.draw_grid(35)
        #self.grid.subsurface.


    def init_vars(self):
        self.neuro_single_times = []
        self.neuro_avg_time = 1
        self.update_single_times = []
        self.update_avg_time = 1
        self.draw_single_times = []
        self.draw_avg_time = 1
        self.physics_single_times = []
        self.physics_avg_time = 1
        self.project_name = None
        self.creature_list:     list[Creature] = []
        self.plant_list:        list[Plant] = []
        self.meat_list:         list[Meat] = []
        self.rocks_list:        list[Rock] = []
        self.spike_list:        list[Spike] = []
        self.wall_list:         list[Wall] = []
        self.lands = []
        self.rocks_checked: bool=False
        self.first_run: bool=True
        self.sel_idx = 0
        self.FPS = 30
        self.dt = 1/self.FPS
        self.running = True
        self.render: bool=True
        self.show_network = True
        self.net_redraw: bool = False
        self.show_specie_name = True
        self.show_dist_and_ang = False
        self.follow: bool=False
        self.selected = None
        self.time = 0
        self.cycles = 0
        self.ranking1 = []
        self.ranking2 = []
        self.last_save_time = 0
        self.herbivores = 0
        self.carnivores = 0
        self.creatures_num = 0
        self.creatures_on_screen = deque(range(30))
        self.plants_on_screen = deque(range(30))
        self.meats_on_screen = deque(range(30))
        self.rocks_on_screen = deque(range(30))
        self.populations = {'plants': [], 'herbivores': [], 'carnivores': []}
        self.mutations = {'added_nodes': [0], 'deleted_nodes': [0], 'added_links': [0], 'deleted_links': [0]}
        self.creatures = {'size': [5], 'speed': [5], 'food': [5], 'power': [5], 'mutations': [5], 'vision': [5]}
        self.neuros = {'nodes': [], 'links': []}
        self.fitness = {'points': [], 'lifetime': []}
        self.map_time = 0.0
        self.follow_time: float = 0.0

    def create_rock(self, vert_num: int, size: int, position: Vec2d):
        rock: Rock=Rock(self.space, vert_num, size, position, 2)
        self.rocks_list.append(rock)
        
    def create_enviro(self):
        self.time = 0
        self.cycles = 0
        self.rocks_checked=False
        self.first_run=True
        self.kill_all_creatures()
        self.kill_all_plants()
        self.kill_things()
        """ edges = [(0, 0), (cfg.WORLD[0]-1, 0), (cfg.WORLD[0]-1, cfg.WORLD[1]-1), (0, cfg.WORLD[1]-1), (0, 0)]
        for e in range(4):
            p1 = edges[e]
            p2 = edges[e+1]
            wall = self.add_wall(p1, p2, 5)
            self.wall_list.append(wall) """
        self.create_borders()
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
        for _ in range(rock_num):
            self.create_rock(randint(cfg.ROCK_VERT_MIN, cfg.ROCK_VERT_MAX), randint(cfg.ROCK_SIZE_MIN, cfg.ROCK_SIZE_MAX), random_position(cfg.WORLD))

    def create_plants(self, plant_num: int):
        for _p in range(plant_num):
            plant = self.add_plant(mature=False, rnd_growth=True)
            self.plant_list.append(plant)

    def create_empty_world(self):
        self.time = 0
        self.cycles = 0
        self.kill_all_creatures()
        self.kill_all_plants()
        self.kill_things()
        self.project_name = None
        self.last_save_time = 0
        self.populations = {'plants': [], 'herbivores': [], 'carnivores': []}
        self.map_time = 0.0
        self.statistics = Statistics()
        self.statistics.add_collection('populations', ['plants', 'herbivores', 'carnivores', 'all creatures'])

    def check_ranking(self):
        self.ranking1.sort(key=sort_by_fitness, reverse=True)
        i = -1
        unique: list[str]=[]
        to_remove: list=[]
        for rank in self.ranking1:
            i +=1
            if not rank['name'] in unique:
                unique.append(rank['name'])
            else:
                to_remove.append(rank)
        for v in to_remove:
            self.ranking1.remove(v)
        to_remove.clear()

    def check_rocks(self):
        if self.first_run:
            return
        self.rocks_checked=True
        for rock in self.rocks_list:
            if rock.collide_rock:
                self.rocks_checked=False
                rock.position=random_position(cfg.WORLD)

    def add_to_ranking(self, creature: Creature):
        ranking = self.ranking1
        ranking.sort(key=sort_by_fitness, reverse=True)
        for rank in reversed(ranking):
            #if rank['name'] == creature.name or rank['name'] in creature.genealogy:
            if rank['name'] == creature.name or rank['first_one'] in creature.first_one:
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
        if event.key == pygame.K_KP_5:
            self.camera.focus_camera(Vector2(cfg.WORLD[0]//2, cfg.WORLD[1]//2))
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
        if event.key == pygame.K_F1:
            self.show_network = not self.show_network
        if event.key == pygame.K_F2:
            self.draw_debug = not self.draw_debug
        if event.key == pygame.K_F3:
            self.show_specie_name = not self.show_specie_name
        if event.key == pygame.K_F8:
            self.show_dist_and_ang = not self.show_dist_and_ang
        if event.key == pygame.K_F4:
            self.statistics.plot()

        if event.key == pygame.K_F9:
            self.follow = not self.follow
        if event.key == pygame.K_F10:
            self.render = not self.render
        if event.key == pygame.K_F11:
            self.draw_eng_bars = not self.draw_eng_bars
        if event.key == pygame.K_KP_PLUS:
            self.camera.zoom_out()
        if event.key == pygame.K_KP_MINUS:
            self.camera.zoom_in()
        if event.key == pygame.K_KP_MULTIPLY:
            self.camera.reset_zoom()

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

    def is_position_free(self, position: Vector2, size: float, categories: int) -> bool:
        f_shapes = ShapeFilter(group=0, categories=categories)
        veryf_pos = self.space.point_query(position, size, f_shapes)
        if veryf_pos == []:
            return True
        return False

    def free_random_position(self, position: Union[Vec2d, tuple], range: Union[Vec2d, tuple]) ->Vec2d:
        rnd_pos = None
        free_pos = False
        i = 0
        while not free_pos:
            x = randint(0, int(range[0]))*2-range[0]
            y = randint(0, int(range[1]))*2-range[1]
            x = int(position[0])+x
            y = int(position[1])+y
            if (x > 15 and x < cfg.WORLD[0]-15) and (y > 15 and y < cfg.WORLD[1]-15):
                free_pos = True
            #x = clamp(x, cfg.PLANT_EDGE, cfg.WORLD[0]-cfg.PLANT_EDGE)
            #y = clamp(y, cfg.PLANT_EDGE, cfg.WORLD[1]-cfg.PLANT_EDGE)
            rnd_pos = Vec2d(x, y)
            i += 1
            if i > 50:
                return rnd_pos
        return rnd_pos

    def add_creature(self, genome: dict=None, pos: Vec2d=None) -> Creature:
        creature: Creature
        cpos = None
        if pos is None:
            cpos = self.free_random_position(Vec2d(cfg.WORLD[0]/2, cfg.WORLD[1]/2), Vec2d(cfg.WORLD[0]/2, cfg.WORLD[1]/2))
        else:
            cpos = pos
        if genome is None:
            creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=cpos, color0=Color('white'), color1=Color('skyblue'), color2=Color(125, 125, 125, 255), color3=Color('red'))
        else:
            creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=cpos, genome=genome)
            [(an, dn), (al, dl)] = creature.mutations_num
            self.update_mutation_stats(an, dn, al, dl)
            self.update_creatures_stats(creature.size, creature.speed, creature.food, creature.power, creature.mutations, creature.eyes)
            self.update_neuro_stats(creature.neuro.GetAllNodesNum(), creature.neuro.GetLinksNum())
        return creature

    def update_neuro_stats(self, node_num: int, link_num: int):
        self.neuros['nodes'].append(node_num)
        self.neuros['links'].append(link_num)

    def update_creatures_stats(self, size: int, speed: int, food: int, power: int, mutations: int, vision: int):
        self.creatures['size'].append(size)
        self.creatures['speed'].append(speed)
        self.creatures['food'].append(food)
        self.creatures['power'].append(power)
        self.creatures['mutations'].append(mutations)
        self.creatures['vision'].append(vision)

    def update_mutation_stats(self, added_nodes: int, deleted_nodes: int, added_links: int, deleted_links: int):
        self.mutations['added_nodes'].append(added_nodes)
        self.mutations['deleted_nodes'].append(deleted_nodes)
        self.mutations['added_links'].append(added_links)
        self.mutations['deleted_links'].append(deleted_links)

    def add_saved_creature(self, genome: dict):
        creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=random_position(cfg.WORLD), genome=genome)
        self.creature_list.append(creature)

    def add_plant(self, mature: bool=False, rnd_growth: bool=False) -> Plant:
        if mature:
            size = cfg.PLANT_MAX_SIZE
        elif rnd_growth:
            size = randint(1, cfg.PLANT_MAX_SIZE)
        else:
            size = 3
        pos = self.free_random_position(Vec2d(cfg.WORLD[0]/2, cfg.WORLD[1]/2), Vec2d(cfg.WORLD[0]/2, cfg.WORLD[1]/2))
        plant = Plant(screen=self.screen, space=self.space, collision_tag=6, world_size=world,
                      size=size, color0=Color((127, 255, 0)), color1=Color('darkgreen'), color3=Color((110, 50, 9)), position=pos)
        return plant

    def add_local_plant(self, position: tuple, radius: int, mature: bool=False) -> Plant:
        if mature:
            size = cfg.PLANT_MAX_SIZE
        else:
            size = 3
        pos = self.free_random_position(Vec2d(position[0], position[1]), Vec2d(radius, radius))
        plant = Plant(screen=self.screen, space=self.space, collision_tag=6, world_size=world,
                      size=size, color0=Color((127, 255, 0)), color1=Color('darkgreen'), color3=Color((110, 50, 9)), position=pos)
        return plant

    def add_wall(self, point0: tuple, point1: tuple, thickness: float) -> Wall:
        wall = Wall(point0, point1, thickness, Color('yellow'), Color('navy'))
        return wall

    def draw(self):
        draw_time: float=time()
        if self.render:
            if self.follow and self.selected != None:
                self.camera.focus_camera(Vector2(int(self.selected.position.x), int(self.selected.position.y)))
            self.screen.fill(Color('black'))
            coords=self.camera.get_offset_tuple()
            #self.screen.blit(self.grid, [-coords[0], -coords[1]])
            self.draw_rocks()
            self.draw_meat()
            self.draw_plants()
            self.draw_creatures()
            self.draw_spikes()
            self.draw_interface()
            if self.net!=None and self.show_network:
                self.screen.blit(self.net, dest=(5, cfg.SCREEN[1]-self.net.get_height()-5), area=self.net.get_rect(), special_flags=BLEND_ALPHA_SDL2)
        else:
            self.screen.fill(Color('black'))
        draw_time = time() - draw_time
        self.draw_single_times.append(draw_time)
        if len(self.draw_single_times) >= 150:
            self.draw_avg_time = mean(self.draw_single_times)
            self.draw_single_times = []
    
    def draw_creatures(self):
        for creature in self.creature_list:
            if self.selected == creature:
                if self.show_dist_and_ang:
                    dist, x, y = creature.draw_dist(camera=self.camera)
                    self.manager.add_text2(dist, x, y, Color('orange'), False, False, False, True)
            if creature.draw(screen=self.screen, camera=self.camera, selected=self.selected, draw_eng_bars=self.draw_eng_bars):
                if self.show_specie_name:
                    name, x, y = creature.draw_name(camera=self.camera)
                    self.manager.add_text2(name, x, y, Color('skyblue'), False, False, False, True)

    def draw_plants(self):
        for plant in self.plant_list:
            plant.draw(screen=self.screen, camera=self.camera, selected=self.selected)

    def draw_meat(self):
        for meat in self.meat_list:
            meat.draw(screen=self.screen, camera=self.camera, selected=self.selected)

    def draw_rocks(self):
        for wall in self.wall_list:
            wall.draw(screen=self.screen, camera=self.camera)

        for rock in self.rocks_list:
            rock.draw(screen=self.screen, camera=self.camera)

    def draw_interface(self):
        #if self.net_timer >= cfg.MEM_TIME:
        #    self.net_timer = self.net_timer%cfg.MEM_TIME
        self.draw_network()
        self.draw_texts()
        self.manager.draw_gui(screen=self.screen)

    def draw_texts(self):
        for txt, rect in self.manager.text_list:
            self.screen.blit(txt, rect)
        self.manager.text_list.clear()

    def draw_network(self):
        if self.show_network:
            if self.selected != None:
                if isinstance(self.selected, Creature):
                    #self.manager.draw_net(self.selected.neuro)
                    if self.selected.brain_just_used:
                        self.net = self.manager.draw_net(network=self.selected.neuro)
                else:
                    self.net=None
            else:
                self.net=None

    def draw_spikes(self):
        for spike in self.spike_list:
            spike.draw(self.screen, self.camera)

    def calc_time(self):
        self.time += self.dt*0.1
        if self.time > 100000:
            self.cycles += 1
            self.time = self.time % 100000

    def get_time(self, digits: int = None):
        return self.cycles*100000 + round(self.time, digits)

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
            wall.kill()
        self.wall_list = []
        for rock in self.rocks_list:
            rock.kill(self.space)
        self.rocks_list = []

    def update(self):
        update_time: float = time()
        self.calc_time()
        if not self.rocks_checked:
            self.check_rocks()
        self.update_creatures(self.dt)
        self.update_plants(self.dt)
        self.update_meat(self.dt)
        self.update_spikes(self.dt)
        self.manager.update_gui(self.dt, self.ranking1)
        self.update_statistics()
        update_time = time()-update_time
        self.update_single_times.append(update_time)
        if len(self.update_single_times) >= 150:
            self.update_avg_time = mean(self.update_single_times)-self.neuro_avg_time
            self.update_single_times = []

    def update_meat(self, dT: float):
        to_kill: list[Meat]=[]
        for meat in self.meat_list:
            meat.update(dT, self.selected)
            if meat.life_time <= 0 or meat.energy <= 0:
                to_kill.append(meat)
        
        for m in to_kill:
            m.kill(self.space)
            self.meat_list.remove(m)

        to_kill.clear()

    def update_creatures_death(self, dt: float):
        ### CHECK ENERGY ###
        for creature in self.creature_list:
            if creature.energy <= 0:
                creature.life2fit()
                self.fitness['points'].append(creature.fitness)
                self.fitness['lifetime'].append(creature.life_time)
                self.add_to_ranking(creature)
                pos = creature.position
                size = ceil(creature.size)
                eng = round(creature.max_energy)
                for _ in range(1):
                    new_pos = self.free_random_position(pos, Vec2d(0, 0))
                    meat = Meat(screen=self.screen, space=self.space, position=new_pos, collision_tag=10, energy=int(eng))
                    self.meat_list.append(meat)
                creature.kill(self.space)
                self.creature_list.remove(creature)

    def update_creatures_analize(self):
        ### ANALIZE ###
        neuro_time = time()
        for creature in self.creature_list:
            creature.brain_just_used=False
            creature.analize()
        neuro_time = time()-neuro_time
        self.neuro_single_times.append(neuro_time)
        if len(self.neuro_single_times) >= 150:
            self.neuro_avg_time = mean(self.neuro_single_times)
            self.neuro_single_times = []

    def creature_edges_reach_check(self, creature: Creature):
        if creature.position.x >= cfg.WORLD[0]+10:
            creature.position.x = 0
        elif creature.position.x <= -10:
            creature.position.x = cfg.WORLD[0]

        if creature.position.y >= cfg.WORLD[1]+10:
            creature.position.y = 0
        elif creature.position.y <= -10:
            creature.position.y = cfg.WORLD[1]

    def update_creature_population(self, dt: float):
        ### REPRODUCE ###
        temp_list = []
        overpopulation = self.creatures_num-cfg.REP_TIME
        if overpopulation < 0:
            overpopulation = 0
        for creature in self.creature_list:
            creature.update(dt=dt, selected=self.selected)
            spike = creature.is_shooting(self.space)
            if isinstance(spike, list):
                self.spike_list.extend(spike)
                #self.spike_list.append(spike)
            #if len(self.creature_list) >= cfg.CREATURE_MAX_NUM:
            #    continue
            if creature.check_reproduction(dt):
                for _ in range(cfg.CHILDS_NUM):
                    genome, position = creature.reproduce(screen=self.screen, space=self.space)
                    new_position = self.free_random_position(position=position, range=Vec2d(cfg.CREATURES_SEP, cfg.CREATURES_SEP))
                    new_creature = Creature(screen=self.screen, space=self.space, time=self.get_time(), collision_tag=2, position=new_position, genome=genome)
                    temp_list.append(new_creature)

        if random() <= cfg.CREATURE_MULTIPLY*self.dt:
            creature = self.add_random_creature()
            self.creature_list.append(creature)

        for new_one in temp_list:
            self.creature_list.append(new_one)
        temp_list = []
        self.check_populatiom()

    def update_creatures(self, dt: float):
        self.update_creatures_death(dt)
        self.update_creatures_analize()
        self.update_creature_population(dt)
        for creature in self.creature_list:
            if creature.check_edges_needed:
                creature.check_edges_needed = False
                self.creature_edges_reach_check(creature)

    def update_spikes(self, dt: float):
        kill_list: list[Spike] = []
        for spike in self.spike_list:
            if not spike.update(dt):
                kill_list.append(spike)

        for spike in kill_list:
            self.spike_list.remove(spike)
            spike.kill(self.space)

        kill_list.clear()

    def update_statistics(self):
        last = self.statistics.get_last_time('populations')
        t = int(self.get_time())
        if t >= int(last+cfg.STAT_PERIOD):
            for key in self.populations:
                if self.populations[key] == []:
                    self.populations[key] = [0]
            p = round(mean(self.populations['plants']))
            h = round(mean(self.populations['herbivores']))
            c = round(mean(self.populations['carnivores']))
            data = {
                'plants': p, 
                'herbivores': h, 
                'carnivores': c,
                'all': h+c
            }
            self.statistics.add_data('populations', last+cfg.STAT_PERIOD, data)
            data = {}
            if self.creatures['size'] == []:
                self.creatures = {'size': [5], 'speed': [5], 'food': [5], 'power': [5], 'mutations': [5], 'vision': [5]}
            data = {
                'size': round(mean(self.creatures['size']), 2),
                'speed': round(mean(self.creatures['speed']), 2),
                'power': round(mean(self.creatures['power']), 2),
                'food': round(mean(self.creatures['food']), 2),
                'mutations': round(mean(self.creatures['mutations']), 2),
                'vision': round(mean(self.creatures['vision']), 2)
            }
            self.populations = {'plants': [], 'herbivores': [], 'carnivores': [], 'all': []}
            self.mutations = {'added_nodes': [], 'deleted_nodes': [], 'added_links': [], 'deleted_links': []}
            self.creatures = {'size': [], 'speed': [], 'food': [], 'power': [], 'mutations': [], 'vision': []}
            self.statistics.add_data('creatures', last+cfg.STAT_PERIOD, data)
            if self.neuros['nodes'] == []:
                self.neuros = {'nodes': [14], 'links': [8]}
            data = {}
            data = {
                'nodes': round(mean(self.neuros['nodes']), 2),
                'links': round(mean(self.neuros['links']), 2)
            }
            self.statistics.add_data('neuros', last+cfg.STAT_PERIOD, data)
            self.neuros = {'nodes': [], 'links': []}
            data = {}
            if len(self.fitness['points']) == 0:
                self.fitness['points'].append(0)
            if len(self.fitness['lifetime']) == 0:
                self.fitness['lifetime'].append(0)
            data = {
                'points': round(mean(self.fitness['points']), 2),
                'lifetime': round(mean(self.fitness['lifetime']), 2)
            }
            self.statistics.add_data('fitness', last+cfg.STAT_PERIOD, data)
            self.fitness = {'points': [], 'lifetime': []}
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
            if plant.check_reproduction():
                if len(self.plant_list) >= cfg.PLANT_MAX_NUM:
                    continue
                new_plant = self.add_local_plant(plant.position, cfg.PLANT_RANGE, False)
                self.plant_list.append(new_plant)
                plant.energy *= 0.5
        if len(self.plant_list) < cfg.PLANT_MIN_NUM:
            plant = self.add_plant()
            self.plant_list.append(plant)

    def physics_step(self, dt: float):
        #for _ in range(1):
        self.space.step(dt)

    def clock_step(self):
        pygame.display.flip()
        self.dt = self.clock.tick(cfg.FPS)/1000*cfg.TIME
        time = self.cycles*100000 + round(self.time)
        self.display_caption(time)

    def display_caption(self, time):
        _fps = round(self.clock.get_fps())
        _dt = round(self.dt*1000)
        if _fps < 100:
            _fps = ' '+str(_fps)
        else:
            _fps = str(_fps)
        if _dt < 100:
            _dt = ' '+str(_dt)
        else:
            _fps = str(_fps)
        total: int = self.herbivores+self.carnivores
        txt = f"[{TITLE}]     [TIME: {time}s]     [fps: {_fps}]     [dT: {_dt}ms]     [herbs: {self.herbivores}]     [hunters: {self.carnivores}]     [all: {total}]     [plants: {len(self.plant_list)}]     [update: {round(self.update_avg_time*1000, 1)}ms]     [neuro: {round(self.neuro_avg_time*1000, 1)}ms]     [physics: {round(self.physics_avg_time*1000, 1)}ms]     [draw: {round(self.draw_avg_time*1000, 1)}ms]"
        pygame.display.set_caption(txt)

    def check_populatiom(self):
        self.check_creature_types()

        if len(self.creature_list) < cfg.CREATURE_MIN_NUM:
            creature = self.add_random_creature()
            self.creature_list.append(creature)

    def add_random_creature(self) -> Creature:
        r = randint(0, 1)
        creature: Creature = None
        if r == 0 or len(self.ranking1) == 0:
            creature = self.add_creature()
        else:
            #ranking = choice([self.ranking1, self.ranking2])
            ranking = self.ranking1
            rank_size = len(ranking)
            rnd = randint(0, rank_size-1)
            genome = deepcopy(ranking[rnd])
            ranking[rnd]['fitness'] -= round(ranking[rnd]['fitness']*cfg.RANK_DECAY)
            creature = self.add_creature(genome)
        return creature

    def auto_save(self):
        if floor((self.cycles*100000+self.time)-self.last_save_time) >= cfg.AUTO_SAVE_TIME:
            self.manager.save_project()
            self.last_save_time = round((self.cycles*100000+self.time), 1)
    
    def set_icon(self, icon_file: str):
        img = image.load(icon_file)
        pygame.display.set_icon(img)

    def main(self):
        set_win_pos(20, 20)
        # self.init(cfg.WORLD)
        self.create_enviro()
        self.set_icon('res\images\logo256.png')
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
            self.first_run=False

    def draw_grid(self, cell_size: int) -> Surface:
        grid: Surface=Surface([cfg.WORLD[0], cfg.WORLD[1]])
        col_num = round(cfg.WORLD[0]/cell_size)
        row_num = round(cfg.WORLD[1]/cell_size)
        pic=self.perlin(col_num, row_num)
        for col in range(col_num):
            for row in range(row_num):
                r = int(255*pic[col][row])
                draw.rect(grid, Color(r,r,r), Rect(cell_size*col, cell_size*row, cell_size-1, cell_size-1), 0)
        return grid

    def perlin(self, col_num: int, row_num: int) -> []:
        noise1 = PerlinNoise(octaves=4)
        noise2 = PerlinNoise(octaves=8)
        noise3 = PerlinNoise(octaves=16)
        noise4 = PerlinNoise(octaves=24)

        xpix, ypix = col_num, row_num
        pic = []
        for i in range(xpix):
            row = []
            for j in range(ypix):
                noise_val = noise1([i/xpix, j/ypix])
                noise_val += 0.5 * noise2([i/xpix, j/ypix])
                noise_val += 0.25 * noise3([i/xpix, j/ypix])
                noise_val += 0.125 * noise4([i/xpix, j/ypix])
                row.append(clamp(noise_val, 0, 1))
            pic.append(row)
        return pic

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
