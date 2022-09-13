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

    def update_gui(self, dt: float, ranking1: list, ranking2: list):
        self.gui.update(dt, ranking1, ranking2)

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
                creature_to_save['neuro'] = creature.neuro.ToJSON()
                creature_to_save['signature'] = deepcopy(creature.signature)
                creature_to_save['genealogy'] = deepcopy(creature.genealogy)
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
                rank_to_save['neuro'] = rank['neuro'].ToJSON()
                rank_to_save['signature'] = deepcopy(rank['signature'])
                rank_to_save['genealogy'] = deepcopy(rank['genealogy'])
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
                rank_to_save['neuro'] = rank['neuro'].ToJSON()
                rank_to_save['signature'] = deepcopy(rank['signature'])
                rank_to_save['genealogy'] = deepcopy(rank['genealogy'])
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
        cr['neuro'] = creature.neuro.ToJSON()
        cr['signature'] = deepcopy(creature.signature)
        cr['genealogy'] = deepcopy(creature.genealogy)
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
        cfg.load_from_file2("saves/" + project_name + "/config.json")
        f = open("saves/" + project_name + "/" + save_name + ".json", "r")
        json_list = f.read()
        obj_list = json.loads(json_list)
        #self.enviro.creature_list.clear()
        self.enviro.create_empty_world()
        self.enviro.create_borders()
        self.enviro.create_rocks(cfg.ROCK_NUM)
        self.enviro.create_plants(cfg.PLANT_INIT_NUM)
        self.project_name = project_name
        self.enviro.project_name = project_name
        self.enviro.time = round(obj_list['time'], 1)
        self.enviro.cycles = obj_list['cycles']
        self.enviro.last_save_time = obj_list['last_save_time']
        #obj_list['ranking1'].sort(key=Sort_By_Fitness, reverse=True)
        #obj_list['ranking2'].sort(key=Sort_By_Fitness, reverse=True)
        self.enviro.ranking1 = []
        self.enviro.ranking2 = []
        for genome in obj_list['creatures']:
            #genome['neuro'] = json.loads(genome['neuro'])
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

    def draw_net(self, network: Network):
        if network:
            last_layer_idx: int=len(network.layers)-1
            h_space = cfg.GRAPH_H
            v_space = cfg.GRAPH_V
            nodes_to_draw = []
            dists = {}
            max_nodes_num = 0
            max_layer_size = 0
            for layer in network.layers:
                node_num = len(network.layers[layer].nodes)
                if max_nodes_num < node_num:
                    max_nodes_num = node_num
            max_layer_size = max_nodes_num * v_space
            max_net_length = len(network.layers)*h_space
            l = 0
            base_line = []

            inp_desc = [
                'ENEMY', 'PLANT', 'MEAT ',
                'ENERG', 'INJUR',
                'ENE-R', 'ENE-D', 
                'FAMIL', 'DNGER',
                'PLA-R', 'PLA-D',
                'MEA-R', 'MEA-D',
                'ROC-R', 'ROC-D',
                'BORD'
            ]
            out_desc = [
                "MOVE", "TURN",
                "EAT", "ATAK",
                "HIDE"
            ]

            for layer in network.layers:
                node_num = len(network.layers[layer].nodes)
                if node_num > 0:
                    dist_nn = round(max_layer_size/(node_num))
                else:
                    dist_nn = max_layer_size
                dists[layer] = dist_nn
                n = 0
                base_line.append(round((cfg.NET_BASE + max_nodes_num * v_space)/2))
                back_box = Rect(4, cfg.SCREEN[1] - (max(base_line))-4, max_net_length+125, max_layer_size+6)
                gfxdraw.aapolygon(self.screen, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color("orange"))
                pygame.draw.polygon(self.screen, Color("orange"), [(back_box.left+1, back_box.top+1), (back_box.right-2, back_box.top+1), (back_box.right-2, back_box.bottom-2), (back_box.left+1, back_box.bottom-2)], 2)
                gfxdraw.filled_polygon(self.screen, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color(0, 0, 0, 35))
                for node_key in network.layers[layer].nodes:
                    node: Node = network.nodes[node_key]
                    v = node.value
                    if node.recurrent:
                        node_color = Color("black")
                    else:
                        if node.activation == ACTIVATION.TANH:
                            node_color = Color("#55ff2f")
                    for link_key in node.to_links:
                        link: Link=network.links[link_key]
                        from_node_key = link.from_node
                        (l0, n0) = network.FindNode(from_node_key)
                        g = 0
                        a = abs(round(200*link.signal))+55
                        if link.signal >= 0:
                            g = 0
                            r = 100+155*link.signal
                            b = 0
                            if link.recombined:
                                g = 255
                        else:
                            b = 100+abs(155*link.signal)
                            r = 0
                            if link.recombined:
                                g = 255
                        link_color = Color((r, g, b, a))
                        w = a//50
                        pygame.draw.line(self.screen, link_color, (80 + l0 * h_space, cfg.SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (80 + l * h_space, cfg.SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)), w)
                    desc = ''
                    nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc, v))
                    n += 1
                l += 1
            out = 0
            for c, l, n, r, d, desc, v in nodes_to_draw:
                v = clamp(v, -1.0, 1.0)
                rv=0; gv = 0; bv=0
                cv = int(6*abs(v))+2
                if v >= 0:
                    gv = 255
                else:
                    rv = 255
                    gv = 150
                    bv = 25
                v_color = Color(rv, gv, bv)
                gfxdraw.aacircle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), cv, v_color)
                gfxdraw.filled_circle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), cv, v_color)
                if r:
                    gfxdraw.filled_circle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), int(cv/2), c)
                    gfxdraw.aacircle(self.screen, 80 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), int(cv/2), c)
                if l == 0:
                    val = network.nodes[network.layers[l].nodes[n]].value
                    text = "{:<2}  {:2> .1f}".format(inp_desc[n], val)
                    self.add_text(text, 6 + l * (h_space+10), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
                elif l == last_layer_idx:
                    val = self.enviro.selected.output[out]
                    text = "{:<}:{:< .1f}".format(out_desc[out], val)
                    self.add_text2(text, 130 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) + 2, Color('white'), False, False, True, False)
                    out += 1
                else:
                    val = network.nodes[network.layers[l].nodes[n]].value
                    text = "{:^1.1f}".format(val)
                    self.add_text(text, 85 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
