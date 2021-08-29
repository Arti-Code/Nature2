from copy import copy, deepcopy
import os
import json
from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame
import pygame.gfxdraw as gfxdraw
from pygame.font import Font, match_font 
from pygame import Surface, Color, Rect
from pymunk import Vec2d, Shape, Circle, Poly
from lib.math2 import flipy, clamp
from lib.net import Network, TYPE, ACTIVATION
from lib.config import cfg
from lib.gui import GUI
from lib.utils import log_to_file

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
        self.gui = GUI(owner=self, view=cfg.WORLD)
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

    def user_event(self, event, dt: float):
        self.gui.process_event(event, dt)

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
            self.add_to_projects_list(project_name)
            i = 0
            project = {}
            creatures = []
            project['name'] = project_name
            project['time'] = self.enviro.get_time()
            project['ranking'] = []
            for creature in self.enviro.creature_list:
                creature_to_save = {}
                creature_to_save['name'] = creature.name
                creature_to_save['gen'] = creature.generation
                creature_to_save['size'] = creature.shape.radius
                creature_to_save['power'] = creature.power
                creature_to_save['meat'] = creature.meat
                creature_to_save['vege'] = creature.vege
                creature_to_save['x'] = round(creature.position.x)
                creature_to_save['y'] = round(creature.position.y)
                creature_to_save['color0'] = [creature.color0.r, creature.color0.g, creature.color0.b, creature.color0.a]
                creature_to_save['color1'] = [creature.color1.r, creature.color1.g, creature.color1.b, creature.color1.a]
                creature_to_save['color2'] = [creature.color2.r, creature.color2.g, creature.color2.b, creature.color2.a]
                creature_to_save['color3'] = [creature.color3.r, creature.color3.g, creature.color3.b, creature.color3.a]
                creature_to_save['neuro'] = creature.neuro.ToJSON()
                creature_to_save['signature'] = deepcopy(creature.signature)
                creatures.append(creature_to_save)
            project['creatures'] = creatures
            for rank in self.enviro.ranking1:
                rank_to_save = {}
                rank_to_save['name'] = copy(rank['name'])
                rank_to_save['gen'] = rank['gen']
                rank_to_save['meat'] = rank['meat']
                rank_to_save['vege'] = rank['vege']
                rank_to_save['size'] = rank['size']
                rank_to_save['fitness'] = rank['fitness']
                rank_to_save['power'] = rank['power']
                rank_to_save['color0'] = [rank['color0'][0], rank['color0'][1], rank['color0'][2], rank['color0'][3]]
                rank_to_save['color1'] = [rank['color1'][0], rank['color1'][1], rank['color1'][2], rank['color1'][3]]
                rank_to_save['color2'] = [rank['color2'][0], rank['color2'][1], rank['color2'][2], rank['color2'][3]]
                rank_to_save['color3'] = [rank['color3'][0], rank['color3'][1], rank['color3'][2], rank['color3'][3]]
                rank_to_save['neuro'] = rank['neuro'].ToJSON()
                rank_to_save['signature'] = deepcopy(rank['signature'])
                project['ranking'].append(rank_to_save)

            if self.add_to_save_list(project_name, str(self.enviro.get_time(1))):
                with open("saves/" + project_name + "/" + str(self.enviro.get_time(1)) + ".json", 'w+') as json_file:
                    json.dump(project, json_file)
                if not json_file.closed:
                    json_file.close()
    
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

    def load_last_state(self, project_name: str):
        f = open("saves/" + project_name + "/saves.json", "r")
        save_list = f.read()
        f.close()
        saves = json.loads(save_list)
        total_num = len(saves["saves"])
        save_name = saves["saves"][total_num - 1]
        self.load_project(project_name, save_name)

    def load_project(self, project_name: str, save_num):
        f = open("saves/" + project_name + "/" + str(save_num) + ".json", "r")
        json_list = f.read()
        obj_list = json.loads(json_list)
        #self.enviro.creature_list.clear()
        self.enviro.create_empty_world(cfg.WORLD)
        self.enviro.create_rocks(cfg.ROCK_NUM)
        self.enviro.create_plants(cfg.PLANT_INIT_NUM)
        self.project_name = project_name
        self.enviro.time = obj_list['time'] % 1000
        self.enviro.cycle = round((obj_list['time'] / 100))
        #obj_list['ranking1'].sort(key=Sort_By_Fitness, reverse=True)
        #obj_list['ranking2'].sort(key=Sort_By_Fitness, reverse=True)
        self.enviro.ranking1 = []
        #self.enviro.ranking2 = []
        for genome in obj_list['creatures']:
            #genome['neuro'] = json.loads(genome['neuro'])
            neuro = Network()
            neuro.FromJSON(genome['neuro'])
            genome['neuro'] = neuro
            self.enviro.add_saved_creature(genome)
        for rank in obj_list['ranking']:
            neuro = Network()
            neuro.FromJSON(rank['neuro'])
            rank['neuro'] = neuro
            self.enviro.ranking1.append(rank)
        if not f.closed:
            f.close()
        log_to_file(project_name+' loaded', 'log.txt')

    def load_last(self, project_name: str):
        f = open("saves/" + project_name + "/saves.json", "r")
        save_list = f.read()
        f.close()
        saves = json.loads(save_list)
        total_num = len(saves["saves"])
        save_name = saves["saves"][total_num - 1]
        self.load_project(project_name, save_name)

    def draw_net(self, network: Network):
        if network:
            h_space = 40
            v_space = 10
            nodes_to_draw = []
            dists = {}
            max_nodes_num = 0
            max_layer_size = 0
            for layer in network.layers:
                node_num = len(network.layers[layer].nodes)
                if max_nodes_num < node_num:
                    max_nodes_num = node_num
            max_layer_size = max_nodes_num * v_space
            l = 0
            base_line = []

            inp_desc = [
                'col_cr', 'col_pl', 'col_ob', 'col_meat', 'angle', 'sid_ang', 'x_pos', 'y_pos', 'eng', 
                'enemy0', 'dist0', 'plant0', 'dist0', 'obst0', 'dist0', 'meat0', 'dist0',
                'enemy1', 'dist1', 'plant1', 'dist1', 'obst1', 'dist1', 'meat1', 'dist1', 
                'enemy2', 'dist2', 'plant2', 'dist2', 'obst2', 'dist2', 'meat2', 'dist2'
            ]
            out_desc = ["mov", "turn", "run", "hid", "atk", "eat"]

            input_keys = network.GetNodeKeyList([TYPE.INPUT])
            output_keys = network.GetNodeKeyList([TYPE.OUTPUT])
            for layer in network.layers:
                last_layer = False
                if network.layers[layer].type == TYPE.OUTPUT:
                    last_layer = True
                node_num = len(network.layers[layer].nodes)
                if node_num > 0:
                    dist_nn = round(max_layer_size/(node_num))
                else:
                    dist_nn = max_layer_size
                dists[layer] = dist_nn
                n = 0
                desc_idx = 0
                base_line.append(round((575 + max_nodes_num * v_space)/2))
                for node_key in network.layers[layer].nodes:
                    node = network.nodes[node_key]
                    if node.recombined:
                        node_color = Color("#8f8f8f")
                    else:
                        if node.activation == ACTIVATION.TANH:
                            node_color = Color("#7CFC00")
                        elif node.activation == ACTIVATION.SIGMOID:
                            node_color = Color("#00f5ed")
                        elif node.activation == ACTIVATION.RELU:
                            node_color = Color("#f50000")
                        elif node.activation == ACTIVATION.LEAKY_RELU:
                            node_color = Color("#ab02e3")
                        elif node.activation == ACTIVATION.BINARY:
                            node_color = Color("#f0f000")
                        elif node.activation == ACTIVATION.REV_BINARY:
                            node_color = Color("#ffaa00")
                        elif node.activation == ACTIVATION.WIDE_BINARY:
                            node_color = Color("#1a8cff")
                        elif node.activation == ACTIVATION.LINEAR:
                            node_color = Color("#f05800")
                    for link_key in node.to_links:
                        link = network.links[link_key]
                        from_node_key = link.from_node
                        (l0, n0) = network.FindNode(from_node_key)
                        g = 0
                        if link.weight >= 0:
                            g = 0
                            r = round(255*link.weight)
                            b = 255 - r
                            if link.recombined:
                                g = 255
                        else:
                            b = abs(round(255*link.weight))
                            r = 255 - b
                            if link.recombined:
                                g = 255
                        link_color = Color(r, g, b)
                        node_num0 = len(network.layers[l0].nodes)
                        pygame.draw.aaline(self.screen, link_color, (80 + l0 * h_space, cfg.SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (80 + l * h_space, cfg.SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)-1))
                        pygame.draw.aaline(self.screen, link_color, (80 + l0 * h_space, cfg.SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (80 + l * h_space, cfg.SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)))
                        pygame.draw.aaline(self.screen, link_color, (80 + l0 * h_space, cfg.SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (80 + l * h_space, cfg.SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)+1))
                    desc = ''
                    nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc))
                    n += 1
                l += 1

            for c, l, n, r, d, desc in nodes_to_draw:
                gfxdraw.filled_circle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), 3, c)
                gfxdraw.aacircle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d + round(d/2), 3, c)
                if r:
                    gfxdraw.aacircle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), 5, c)
                if l == 0:
                    val = network.nodes[network.layers[l].nodes[n]].value
                    self.add_text(f'{inp_desc[n]}: ', 6 + l * (h_space+10), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
                    self.add_text(f'{round(val, 1)}', 50 + l * (h_space+10), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))