import json
import os
from copy import copy, deepcopy
from shutil import rmtree

import pygame
import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface

from lib.config import cfg
from lib.creature import Creature
from lib.gui import GUI
from lib.math2 import clamp
from lib.net import ACTIVATION, Link, Network, Node
from lib.net_draw import draw_net


class Manager:

    def __init__(self, screen: Surface, enviro):
        pygame.font.init()
        self.fira_code = pygame.font.Font("res/fonts/fira.ttf", 12)
        self.creature_font = pygame.font.Font("res/fonts/fira.ttf", 10)
        self.norm_font = pygame.font.Font("res/fonts/fira.ttf", 12)
        self.titl_font = pygame.font.Font("res/fonts/fira.ttf", 18)
        self.subtitl_font = pygame.font.Font("res/fonts/fira.ttf", 16)
        self.small_font = pygame.font.Font("res/fonts/fira.ttf", 8)
        self.titl_font.set_bold(True)
        self.subtitl_font.set_bold(True)
        self.screen = screen
        self.enviro = enviro
        self.gui = GUI(owner=self, view=cfg.SCREEN)
        self.font_small = pygame.font.Font("res/fonts/fira.ttf", 8)
        self.text_list: list = []
        
    def new_project(self, new_name: str):
        self.add_to_project_list(new_name)
        try:
            os.mkdir('saves/' + new_name)
        except FileExistsError:
            pass

    def add_to_project_list(self, new_name: str):
        f = open("saves/projects.json", "r+")
        proj_list = f.read()
        f.close()
        projects_list = json.loads(proj_list)
        if not new_name in projects_list["projects"]:
            projects_list["projects"].append(new_name)
            proj_json = json.dumps(projects_list)
            f = open("saves/projects.json", "w+")
            f.write(proj_json)
            f.close()
            return True
        else:
            return False

    def user_event(self, event, dt: float)->bool:
        if self.gui.process_event(event, dt):
            return True
        return False

    def update_gui(self, dt: float, ranking: list):
        self.gui.update(dt, ranking)

    def draw_gui(self, screen: Surface):
        self.gui.draw_ui(screen)

    def new_sim(self, project_name: str):
       pass 

    def add_text(self, text: str, x: int, y: int, small_font: bool=True, color: Color=Color('white')):
       render_text = self.small_font.render(text, True, color)
       self.screen.blit(render_text, (x, y), )

    def add_text2(self, text, x, y, color, title=False, subtitle=False, creature=False, small=False):
        if title:
            txt_render = self.titl_font.render(text, True, Color(color))
            txt_rect = txt_render.get_rect()
            txt_rect.center = (x, y)
        elif subtitle:
            txt_render = self.subtitl_font.render(text, True, Color(color))
            txt_rect = txt_render.get_rect()
            txt_rect.center = (x, y)
        elif creature:
            txt_render = self.creature_font.render(text, True, Color(color))
            txt_rect = txt_render.get_rect()
            txt_rect.center = (x, y)
        elif small:
            txt_render = self.small_font.render(text, True, Color(color))
            txt_rect = txt_render.get_rect()
            txt_rect.left = x
            txt_rect.top = y
        else:
            txt_render = self.norm_font.render(text, True, Color(color))
            txt_rect = txt_render.get_rect()
            txt_rect.left = x
            txt_rect.top = y
        self.text_list.append((txt_render, txt_rect))

    def save_project(self):
        project_name = self.enviro.project_name
        if project_name != '' and isinstance(project_name, str):
            project = {}
            project['name'] = project_name
            project['time'] = round(self.enviro.time, 1)
            project['cycles'] = self.enviro.cycles
            project['last_save_time'] = self.enviro.cycles*6000+round(self.enviro.time)
            project['creatures'] = []
            for creature in self.enviro.creature_list:
                creature_to_save = {}
                creature_to_save['name'] = creature.name
                creature_to_save['gen'] = creature.generation
                creature_to_save['mutations'] = creature.mutations
                creature_to_save['size'] = creature.shape.radius
                creature_to_save['power'] = creature.power
                creature_to_save['food'] = creature.food
                creature_to_save['speed'] = creature.speed
                creature_to_save['eyes'] = creature.eyes
                creature_to_save['x'] = round(creature.position.x)
                creature_to_save['y'] = round(creature.position.y)
                creature_to_save['color0'] = [creature.color0.r, creature.color0.g, creature.color0.b, creature.color0.a]
                creature_to_save['color1'] = [creature.color1.r, creature.color1.g, creature.color1.b, creature.color1.a]
                creature_to_save['color2'] = [creature.color2.r, creature.color2.g, creature.color2.b, creature.color2.a]
                creature_to_save['color3'] = [creature.color3.r, creature.color3.g, creature.color3.b, creature.color3.a]
                creature_to_save['signature'] = deepcopy(creature.signature)
                creature_to_save['genealogy'] = deepcopy(creature.genealogy)
                creature_to_save['first_one'] = copy(creature.first_one)
                creature_to_save['spike_num'] = creature.spike_num
                creature_to_save['neuro'] = creature.neuro.ToJSON()
                project['creatures'].append(creature_to_save)
            project['ranking1'] = []
            for rank in self.enviro.ranking1:
                rank_to_save = {}
                rank_to_save['name'] = copy(rank['name'])
                rank_to_save['gen'] = rank['gen']
                rank_to_save['food'] = rank['food']
                rank_to_save['speed'] = rank['speed']
                rank_to_save['eyes'] = rank['eyes']
                rank_to_save['mutations'] = rank['mutations']
                rank_to_save['size'] = rank['size']
                rank_to_save['fitness'] = rank['fitness']
                rank_to_save['power'] = rank['power']
                rank_to_save['color0'] = [rank['color0'][0], rank['color0'][1], rank['color0'][2], rank['color0'][3]]
                rank_to_save['color1'] = [rank['color1'][0], rank['color1'][1], rank['color1'][2], rank['color1'][3]]
                rank_to_save['color2'] = [rank['color2'][0], rank['color2'][1], rank['color2'][2], rank['color2'][3]]
                rank_to_save['color3'] = [rank['color3'][0], rank['color3'][1], rank['color3'][2], rank['color3'][3]]
                rank_to_save['signature'] = deepcopy(rank['signature'])
                rank_to_save['genealogy'] = deepcopy(rank['genealogy'])
                rank_to_save['first_one'] = copy(rank['first_one'])
                rank_to_save['spike_num'] = rank['spike_num']
                rank_to_save['neuro'] = rank['neuro'].ToJSON()
                project['ranking1'].append(rank_to_save)
            project['ranking2'] = []
            for rank in self.enviro.ranking2:
                rank_to_save = {}
                rank_to_save['name'] = copy(rank['name'])
                rank_to_save['gen'] = rank['gen']
                rank_to_save['food'] = rank['food']
                rank_to_save['speed'] = rank['speed']
                rank_to_save['eyes'] = rank['eyes']
                rank_to_save['mutations'] = rank['mutations']
                rank_to_save['size'] = rank['size']
                rank_to_save['fitness'] = rank['fitness']
                rank_to_save['power'] = rank['power']
                rank_to_save['color0'] = [rank['color0'][0], rank['color0'][1], rank['color0'][2], rank['color0'][3]]
                rank_to_save['color1'] = [rank['color1'][0], rank['color1'][1], rank['color1'][2], rank['color1'][3]]
                rank_to_save['color2'] = [rank['color2'][0], rank['color2'][1], rank['color2'][2], rank['color2'][3]]
                rank_to_save['color3'] = [rank['color3'][0], rank['color3'][1], rank['color3'][2], rank['color3'][3]]
                rank_to_save['signature'] = deepcopy(rank['signature'])
                rank_to_save['genealogy'] = deepcopy(rank['genealogy'])
                rank_to_save['first_one'] = copy(rank['first_one'])
                rank_to_save['spike_num'] = rank['spike_num']
                rank_to_save['neuro'] = rank['neuro'].ToJSON()
                project['ranking2'].append(rank_to_save)
            project['statistics'] = {}
            project['statistics']['populations'] = self.enviro.statistics.get_collection('populations')
            project['statistics']['creatures'] = self.enviro.statistics.get_collection('creatures')
            project['statistics']['neuros'] = self.enviro.statistics.get_collection('neuros')
            project['statistics']['fitness'] = self.enviro.statistics.get_collection('fitness')
            if self.add_to_save_list(project_name, str(round(self.enviro.get_time(0)))):
                with open("saves/" + project_name + "/" + str(round(self.enviro.get_time(0))) + ".json", 'w+') as json_file:
                    json.dump(project, json_file)
                if not json_file.closed:
                    json_file.close()
    
    def save_creature(self, creature: Creature) -> bool:
        if self.enviro.project_name == None:
            return False
        cr = {}
        cr['name'] = creature.name
        cr['gen'] = creature.generation
        cr['mutations'] = creature.mutations
        cr['size'] = creature.shape.radius
        cr['power'] = creature.power
        cr['food'] = creature.food
        cr['speed'] = creature.speed
        cr['eyes'] = creature.eyes
        cr['color0'] = [creature.color0.r, creature.color0.g, creature.color0.b, creature.color0.a]
        cr['color1'] = [creature.color1.r, creature.color1.g, creature.color1.b, creature.color1.a]
        cr['color2'] = [creature.color2.r, creature.color2.g, creature.color2.b, creature.color2.a]
        cr['color3'] = [creature.color3.r, creature.color3.g, creature.color3.b, creature.color3.a]
        cr['signature'] = deepcopy(creature.signature)
        cr['genealogy'] = deepcopy(creature.genealogy)
        cr['first_one'] = copy(creature.first_one)
        cr['spike_num'] = creature.spike_num
        cr['neuro'] = creature.neuro.ToJSON()
        with open("saves/creatures/"+creature.name+".json", 'w+') as creature_file:
            json.dump(cr, creature_file)
        creature_file.close()
        return True

    def add_to_projects_list(self, project_name: str):
        f = open("saves/projects.json", "r+")
        proj_list = f.read()
        f.close()
        projects_list = json.loads(proj_list)
        if not project_name in projects_list["projects"]:
            projects_list["projects"].append(project_name)
            proj_json = json.dumps(projects_list)
            f = open("saves/projects.json", "w+")
            f.write(proj_json)
            f.close()
            return True
        else:
            return False

    def delete_from_projects_list(self, project_name: str):
        f = open("saves/projects.json", "r+")
        proj_list = f.read()
        f.close()
        projects_list = json.loads(proj_list)
        if project_name in projects_list["projects"]:
            projects_list["projects"].remove(project_name)
            proj_json = json.dumps(projects_list)
            f = open("saves/projects.json", "w+")
            f.write(proj_json)
            f.close()
            return True
        else:
            return False

    def add_to_save_list(self, project_name: str, save_time: str):
        saves_list = {}
        try:
            f = open("saves/" + project_name + "/saves.json", "r")
            save_list = f.read()
            f.close()
            saves_list = json.loads(save_list)
        except FileNotFoundError:
            saves_list["saves"] = []
        if not save_time in saves_list["saves"]:
            saves_list["saves"].append(save_time)
            save_json = json.dumps(saves_list)
            f = open("saves/" + project_name + "/saves.json", "w+")
            f.write(save_json)
            f.close()
            return True
        else:
            return False

    def load_creature(self, name: str="creature"):
        f = open("saves/creatures/" + name + ".json", "r")
        json_cr = f.read()
        f.close()
        obj_cr = json.loads(json_cr)
        neuro = Network()
        neuro.FromJSON(obj_cr['neuro'])
        obj_cr['neuro'] = neuro
        self.enviro.add_saved_creature(obj_cr)

    def load_last_state(self, project_name: str):
        f = open("saves/" + project_name + "/saves.json", "r")
        save_list = f.read()
        f.close()
        saves = json.loads(save_list)
        total_num = len(saves["saves"])
        save_name = saves["saves"][total_num - 1]
        self.load_project(project_name, save_name)

    def load_project(self, project_name: str, save_name: str):
        cfg.load_from_file("saves/" + project_name + "/config.json")
        f = open("saves/" + project_name + "/" + save_name + ".json", "r")
        json_list = f.read()
        obj_list = json.loads(json_list)
        self.enviro.create_empty_world()
        self.enviro.create_borders()
        self.enviro.create_rocks(cfg.ROCK_NUM)
        self.enviro.create_plants(cfg.PLANT_INIT_NUM)
        self.project_name = project_name
        self.enviro.project_name = project_name
        self.enviro.time = round(obj_list['time'], 1)
        self.enviro.cycles = obj_list['cycles']
        self.enviro.last_save_time = obj_list['last_save_time']
        self.enviro.ranking1 = []
        self.enviro.ranking2 = []
        for genome in obj_list['creatures']:
            neuro = Network()
            neuro.FromJSON(genome['neuro'])
            genome['neuro'] = neuro
            self.enviro.add_saved_creature(genome)
        for rank in obj_list['ranking1']:
            neuro = Network()
            neuro.FromJSON(rank['neuro'])
            rank['neuro'] = neuro
            self.enviro.ranking1.append(rank)
        for rank in obj_list['ranking2']:
            neuro = Network()
            neuro.FromJSON(rank['neuro'])
            rank['neuro'] = neuro
            self.enviro.ranking2.append(rank)
        for stat in obj_list['statistics']:
            self.enviro.statistics.load_statistics(stat, obj_list['statistics'][stat])
        if not f.closed:
            f.close()

    def load_last(self, project_name: str):
        path = f"saves/{project_name}"
        saves_iter = os.scandir(path)
        saves = []
        for s in saves_iter:
            if s.is_file() and s.name != "config.json":
                try:
                    save_name = int(s.name.split('.', 1)[0])
                    saves.append(save_name)
                except:
                    continue
        if len(saves) == 0:
            return
        last_save = str(max(saves))
        saves_iter.close()
        self.load_project(project_name, last_save)

    def delete_project(self, sim_name: str) -> bool:
        res = True
        try:
            rmtree('saves/' + sim_name)
        except:
            res = False
        finally:
            return res

    def delete_creature(self, name: str) -> bool:
        res = True
        try:
            os.remove('saves/creatures/' + name + '.json')
        except:
            res = False
        finally:
            return res

    def draw_net(self, network: Network):
        draw_net(self.screen, self, network)