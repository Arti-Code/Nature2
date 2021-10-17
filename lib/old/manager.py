import os
import json
import svgwrite
import numpy as np
from random import random, randint, choice
import math
import pygame.gfxdraw as gfxdraw
import pygame as pg
from pygame import Rect, Color
from statistics import mean
import pygame_gui
from copy import deepcopy, copy
from lib.math2 import *
from lib.config import *
from lib.net import Network, Node, Link, Layer, TYPE, ACTIVATION
from lib.config import *
from lib.gui import GUI
from lib.viewport import Viewport


class Manager():

    def __init__(self, screen, enviro):
    
        self.screen = screen
        self.enviro = enviro
        pg.font.init()
        self.fira_code = pg.font.Font("res/fonts/fira.ttf", 12)
        self.creature_font = pg.font.Font("res/fonts/fira.ttf", 10)
        self.norm_font = pg.font.Font("res/fonts/fira.ttf", 12)
        self.titl_font = pg.font.Font("res/fonts/fira.ttf", 18)
        self.subtitl_font = pg.font.Font("res/fonts/fira.ttf", 16)
        self.small_font = pg.font.Font("res/fonts/fira.ttf", 8)
        self.titl_font.set_bold(True)
        self.subtitl_font.set_bold(True)
        self.text_list = []
        self.last_save = 0
        self.w = cfg['WIDTH']
        self.h = cfg['HEIGHT']
        self.view = Viewport(screen, self.w, self.h)
        self.project_name = ''
        self.scr_x = 1
        self.scr_y = 1
        self.scr_rect = Rect(self.scr_y, self.scr_x, self.h, self.w)
        self.cfg_params = False
        self.cfg_index = 0
        self.GUI = GUI(self, self.view)
        self.moved_screen = True

    def Update(self):
        self.moved_screen = False

    #def MoveScreen(self, dx, dy):
    #    self.view.move(Vector2(dx, dy))
    #    self.moved_screen = True

    def NewProject(self, new_name: str):
        self.AddToProjectsList(new_name)
        try:
            os.mkdir('saves/' + new_name)
        except FileExistsError:
            pass

    def AddToProjectsList(self, new_name: str):
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

    def SaveProject(self, project_name: str):
        if project_name != '' and isinstance(project_name, str):
            self.AddToProjectsList(project_name)
            i = 0
            project = {}
            project['name'] = project_name
            #project['time'] = self.enviro.Time()
            project['ranking1'] = []
            project['ranking2'] = []
            #ranking = self.enviro.ranking1
            #for r in ranking:
            #    network = r['neuro'].ToJSON()
            #    spec = r['species'].ToJSON()
            #    creature = {}
            #    creature['name'] = r['name']
            #    creature['points'] = r['fitness']
            #    creature['food'] = r['food']
            #    creature['size'] = r['size']
            #    creature['gen'] = r['gen']
            #    creature['power'] = r['power']
            #    creature['sprint'] = r['sprint']
            #    creature['recombine'] = r['recombine']
            #    creature['mutate'] = r['mutate']
            #    creature['neuro'] = network
            #    creature['species'] = spec
            #    project['ranking1'].append(creature)

            #ranking = self.enviro.ranking2
            #for r in ranking:
            #    network = r['neuro'].ToJSON()
            #    spec = r['species'].ToJSON()
            #    creature = {}
            #    creature['name'] = r['name']
            #    creature['points'] = r['fitness']
            #    creature['food'] = r['food']
            #    creature['size'] = r['size']
            #    creature['gen'] = r['gen']
            #    creature['power'] = r['power']
            #    creature['sprint'] = r['sprint']
            #    creature['recombine'] = r['recombine']
            #    creature['mutate'] = r['mutate']
            #    creature['neuro'] = network
            #    creature['species'] = spec
            #    project['ranking2'].append(creature)
            #self.SaveStats(project_name)
            if self.AddToSaveList(project_name, str(self.enviro.Time())):
                with open("saves/" + project_name + "/" + str(self.enviro.Time()) + ".json", 'w+') as json_file:
                    json.dump(project, json_file)
                if not json_file.closed:
                    json_file.close()

    def SaveStats(self, project_name: str) -> None:
        stats = {}
        stats['herbs'] = json.dumps(self.enviro.borns['herbs'])
        stats['preds'] = json.dumps(self.enviro.borns['preds'])
        stats['all'] = json.dumps(self.enviro.borns['all'])
        stats['food'] = json.dumps(self.enviro.stats['food'])
        stats['size'] = json.dumps(self.enviro.stats['size'])
        stats['power'] = json.dumps(self.enviro.stats['power'])
        stats['speed'] = json.dumps(self.enviro.stats['speed'])
        stats['mutations'] = json.dumps(self.enviro.stats['mutations'])
        stats['recombinations'] = json.dumps(self.enviro.stats['recombinations'])
        stats['fitness'] = json.dumps(self.enviro.stats['fitness'])
        stats['herb_fit'] = json.dumps(self.enviro.stats['herb_fit'])
        stats['pred_fit'] = json.dumps(self.enviro.stats['pred_fit'])
        with open("saves/" + project_name + "/stats.json", 'w+') as json_file:
            json.dump(stats, json_file)
        json_file.close()

    def AddToSaveList(self, project_name, save_name):
        saves_list = {}
        try:
            f = open("saves/" + project_name + "/saves.json", "r")
            save_list = f.read()
            f.close()
            saves_list = json.loads(save_list)
        except FileNotFoundError:
            saves_list["saves"] = []
        if not save_name in saves_list["saves"]:
            saves_list["saves"].append(save_name)
            save_json = json.dumps(saves_list)
            f = open("saves/" + project_name + "/saves.json", "w+")
            f.write(save_json)
            f.close()
            return True
        else:
            return False

    def Quit(self):
        pg.quit()

    def LoadSaveMenu(self):
        f = open("saves/projects.json", "r")
        projects_list = f.read()
        f.close()
        projects = json.loads(projects_list)
        return projects["projects"]

    def LoadLast(self, project_name: str):
        f = open("saves/" + project_name + "/saves.json", "r")
        save_list = f.read()
        f.close()
        saves = json.loads(save_list)
        total_num = len(saves["saves"])
        save_name = saves["saves"][total_num - 1]
        self.LoadProject(project_name, save_name)

    def LoadProject(self, project_name: str, save_num):
        f = open("saves/" + project_name + "/" + str(save_num) + ".json", "r")
        json_list = f.read()
        obj_list = json.loads(json_list)
        self.enviro.my_creatures.clear()
        self.enviro.CreateWorld(0.03, False)
        self.project_name = copy(project_name)
        self.enviro.time = obj_list['time'] % 100
        self.enviro.cycle = round((obj_list['time'] - self.enviro.time) / 100)
        self.enviro.stats_time = round(self.enviro.time, 1)
        obj_list['ranking1'].sort(key=Sort_By_Fitness, reverse=True)
        obj_list['ranking2'].sort(key=Sort_By_Fitness, reverse=True)
        self.enviro.ranking1 = []
        self.enviro.ranking2 = []
        i = 0
        for c in obj_list['ranking1']:
            r = {}
            neuro = Network()
            neuro.FromJSON(c['neuro'])
            r['neuro'] = neuro
            species = Species()
            species.FromJSON(c['species'])
            r['species'] = species
            r['name'] = copy(c['name'])
            r['size'] = c['size']
            r['food'] = c['food']
            r['gen'] = c['gen']
            r['power'] = c['power']
            r['sprint'] = c['sprint']
            r['fitness'] = c['points']
            r['recombine'] = c['recombine']
            r['mutate'] = c['mutate']
            self.enviro.ranking1.append(r)
            i += 1
        i = 0
        for c in obj_list['ranking2']:
            r = {}
            neuro = Network()
            neuro.FromJSON(c['neuro'])
            r['neuro'] = neuro
            species = Species()
            species.FromJSON(c['species'])
            r['species'] = species
            r['name'] = copy(c['name'])
            r['size'] = c['size']
            r['food'] = c['food']
            r['gen'] = c['gen']
            r['power'] = c['power']
            r['sprint'] = c['sprint']
            r['fitness'] = c['points']
            r['recombine'] = c['recombine']
            r['mutate'] = c['mutate']
            self.enviro.ranking2.append(r)
            i += 1
        self.last_save = self.enviro.Time()
        self.enviro.load_moment = True
        if not f.closed:
            f.close()
        self.LoadStats(project_name)

    def LoadStats(self, project_name: str) -> None:
        f = open("saves/" + project_name + "/stats.json", "r")
        json_stats = f.read()
        f.close()
        obj_stats = json.loads(json_stats)
        self.enviro.borns = {}
        self.enviro.stats = {}
        self.enviro.borns['herbs'] = json.loads(obj_stats['herbs'])
        self.enviro.borns['preds'] = json.loads(obj_stats['preds'])
        self.enviro.borns['all'] = json.loads(obj_stats['all'])
        self.enviro.stats['food'] = json.loads(obj_stats['food'])
        self.enviro.stats['size'] = json.loads(obj_stats['size'])
        self.enviro.stats['power'] = json.loads(obj_stats['power'])
        self.enviro.stats['speed'] = json.loads(obj_stats['speed'])
        self.enviro.stats['mutations'] = json.loads(obj_stats['mutations'])
        self.enviro.stats['recombinations'] = json.loads(obj_stats['recombinations'])
        self.enviro.stats['fitness'] = json.loads(obj_stats['fitness'])
        self.enviro.stats['herb_fit'] = json.loads(obj_stats['herb_fit'])
        self.enviro.stats['pred_fit'] = json.loads(obj_stats['pred_fit'])

    def ShowMenu(self, menu_dict):
        i = 0
        total = len(menu_dict)
        base_pos = total / 2 * 60
        for row in menu_dict:
            if i == self.pos:
                self.func = menu_dict[row][1]
                self.param = menu_dict[row][2]
                self.AddText(menu_dict[row][0], cfg['WIDTH'] / 2, (cfg['HEIGHT']/2 + i * 60)-base_pos, "green", title=True)
            else:
                self.AddText(menu_dict[row][0], cfg['WIDTH'] / 2, (cfg['HEIGHT']/2 + i * 60)-base_pos, "ghostwhite", title=True)
            i += 1

    def ShowConfig(self, index: int=0):
        self.cfg_params = True
        cfg_list = []
        cfg_list = cfg.keys()
        return cfg_list[index]

    def NetToSVG(self, network: Network, name: str, file_path: str):
        if network and name and file_path:
            file_path = file_path + '/' + name + '.svg'
            cvs = svgwrite.Drawing(file_path, size=(600, 700))
            cvs.add(cvs.rect(size=(600, 700), fill='black'))
            cvs.add(cvs.text(name, insert=(250,20), fill='white'))
            h_space = 50
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
            for layer in network.layers:
                node_num = len(network.layers[layer].nodes)
                if node_num > 0:
                    dist_nn = round(max_layer_size/(node_num))
                else:
                    dist_nn = max_layer_size
                dists[layer] = dist_nn
                n = 0
                base_line.append(round((max_nodes_num * v_space)/2))
                for node_key in network.layers[layer].nodes:
                    node = network.nodes[node_key]
                    if node.recombined:
                        node_color = (64, 224, 208)
                        #node_color = 'violet'
                    else:
                        if node.activation == ACTIVATION.TANH:
                            node_color = (0, 255, 0)
                            #node_color = 'green'
                        elif node.activation == ACTIVATION.SIGMOID:
                            node_color = (0, 191, 255)
                            #node_color = 'blue'
                        elif node.activation == ACTIVATION.RELU:
                            node_color = (255, 0, 0)
                            #node_color = 'red'
                        elif node.activation == ACTIVATION.LEAKY_RELU:
                            node_color = (255, 20, 147)
                            #node_color = 'pink'
                        elif node.activation == ACTIVATION.BINARY:
                            node_color = (255, 255, 0)
                            #node_color = 'yellow'
                    for link_key in node.to_links:
                        link = network.links[link_key]
                        from_node_key = link.from_node
                        (l0, n0) = network.FindNode(from_node_key)
                        w_color = abs(round(155*link.weight)) + 100
                        if link.weight >= 0:
                            if link.recombined:
                                link_color = svgwrite.rgb(51, 204, 51)
                            else:
                                link_color = svgwrite.rgb(w_color, round(w_color/3), round(w_color/3))
                        else:
                            if link.recombined:
                                link_color = svgwrite.rgb(51, 204, 51)
                            else:
                                link_color = svgwrite.rgb(round(w_color/3), round(w_color/3), w_color)
                        node_num0 = len(network.layers[l0].nodes)
                        cvs.add(cvs.line((50 + l0 * h_space, 50 + (dists[l0] * n0) + round(dists[l0]/2)), (50 + l * h_space, 50 + (dist_nn * n) + round(dist_nn/2)), stroke=link_color))
                    nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn))
                    n += 1
                l += 1

            for c, l, n, r, d in nodes_to_draw:
                x = 50 + l * h_space
                y = 50 + d*n + round(d/2)
                if r:
                    cvs.add(cvs.circle((x, y), 6, fill=svgwrite.rgb(c[0], c[1], c[2], '%')))
                    cvs.add(cvs.circle((x, y), 4, fill=svgwrite.rgb(255, 255, 255, '%')))
                    cvs.add(cvs.circle((x, y), 2, fill=svgwrite.rgb(c[0], c[1], c[2], '%')))
                else:
                    cvs.add(cvs.circle((x, y), 4, fill=svgwrite.rgb(c[0], c[1], c[2], '%')))
            cvs.save(pretty=True)
            return True
        else:
            return False

    def SaveCreature(self, creature):
        f = open("saves/creatures.json", "r")
        cr_list_json = f.read()
        f.close()
        cr_list = json.loads(cr_list_json)
        creature2 = {}
        creature2['name'] = creature.name
        creature2['food'] = creature.food
        creature2['size'] = creature.size
        creature2['gen'] = creature.gen
        creature2['power'] = creature.power
        creature2['sprint'] = creature.sprint
        creature2['recombine'] = creature.recombine
        creature2['mutate'] = creature.mutate
        creature2['neuro'] = creature.neuro.ToJSON()
        creature2['species'] = creature.species.ToJSON()
        cr_list['creatures'].append(creature2)
        cr_list_json = json.dumps(cr_list)
        f = open("saves/creatures.json", "w")
        f.write(cr_list_json)
        f.close()
        #print(f"{self.enviro.Time(1)}: creature has been saved")

    def LoadCreature(self, dt: float):
        f = open("saves/creatures.json", "r")
        cr_list_json = f.read()
        f.close()
        cr = None
        cr_list = json.loads(cr_list_json)
        cr = choice(cr_list["creatures"])
        neuro = Network()
        neuro.FromJSON(cr['neuro'])
        cr['neuro'] = neuro
        species = Species()
        species.FromJSON(cr['species'])
        cr['species'] = species
        creature = Creature(enviro=self.enviro, view=self.view, dT=dt, screen=self.screen, size=cr["size"], parent1=cr)
        self.enviro.my_creatures.append(creature)
        #print(f"{self.enviro.Time(1)}: creature loaded from file")

    def DrawNet(self, network: Network):
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

            inp_desc = ["sid", 
                        "lpd", "lps", "lcd", "lcs", "lca", "lmd", "lms", "lob",
                        "fpd", "fps", "fcd", "fcs", "fca", "fmd", "fms", "fob",
                        "rpd", "rps", "rcd", "rcs", "rca", "rmd", "rms", "rob",
                        "eng", "atk", "hrt", "hid", "enmy", "good", "run", "stam",
                         "collid", "x", "y"]
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
                        pg.draw.aaline(self.screen, link_color, (40 + l0 * h_space, cfg['HEIGHT'] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, cfg['HEIGHT'] - base_line[l] + (dist_nn * n) + round(dist_nn/2)-1))
                        pg.draw.aaline(self.screen, link_color, (40 + l0 * h_space, cfg['HEIGHT'] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, cfg['HEIGHT'] - base_line[l] + (dist_nn * n) + round(dist_nn/2)))
                        pg.draw.aaline(self.screen, link_color, (40 + l0 * h_space, cfg['HEIGHT'] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, cfg['HEIGHT'] - base_line[l] + (dist_nn * n) + round(dist_nn/2)+1))
                    #if last_layer:
                    #    desc = out_desc[desc_idx]
                    #    desc_idx += 1
                    desc = ''
                    nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc))
                    n += 1
                l += 1

            for c, l, n, r, d, desc in nodes_to_draw:
                gfxdraw.filled_circle(self.screen, 40 + l * h_space, cfg['HEIGHT'] - base_line[l] + d*n + round(d/2), 3, c)
                gfxdraw.aacircle(self.screen, 40 + l * h_space, cfg['HEIGHT'] - base_line[l] + d + round(d/2), 3, c)
                if r:
                    gfxdraw.aacircle(self.screen, 40 + l * h_space, cfg['HEIGHT'] - base_line[l] + d*n + round(d/2), 5, c)
                if l == 0:
                    self.AddText(f'{n}', 20 + l * (h_space+10), cfg['HEIGHT'] - base_line[l] + d*n + round(d/2) - 5, Color('white'), small=True)
                if desc:
                    self.AddText(desc, 40 + l * (h_space+10), cfg['HEIGHT'] - base_line[l] + d*n + round(d/2), Color('#069ab8'), small=True)
    def AutoSave(self):

        if self.project_name != '':
            if self.enviro.Time() % cfg['AUTOSAVE_TIME'] == 0 and self.enviro.Time() > self.last_save:
                self.SaveProject(self.project_name)
                self.last_save = self.enviro.Time()
                self.enviro.species.save_to_file(self.project_name, self.enviro.TimeRound())

    def AddText(self, text, x, y, color, title=False, subtitle=False, creature=False, small=False):

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

    def Events(self, dT: float):
        for event in pg.event.get():
            self.GUI.process_event(event, dT)
                
            #   ***QUIT EVENT***
            if event.type == pg.QUIT:
                self.enviro.running = False

            #   ***MOUSE EVENTS***
            if event.type == pg.MOUSEBUTTONDOWN:
                self.MouseEvent(event)
            #   ***KEY EVENTS***
            if event.type == pg.KEYDOWN:
                self.KeyEvent(event, dT)

        self.GUI.update(dT)

    def GuiEvent(self, event):
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == '#menu_btn':
                self.show_menu = not self.show_menu
                if self.show_menu:
                    self.menu_win.show()
                else:
                    self.menu_win.hide()

    def MouseEvent(self, event):
            if self.enviro.selected:
                self.enviro.selected = None
            (mouseX, mouseY) = pg.mouse.get_pos()
            self.enviro.selected = self.enviro.FindCreature(self.enviro.my_creatures, mouseX, mouseY)
            if self.enviro.selected:
                pass

    def KeyEvent(self, event, dt: float):
            if event.key == pg.K_KP6 or event.key == pg.K_KP4:
                old_sel_index = self.enviro.sel_index
                if event.key == pg.K_KP6:
                    self.enviro.sel_index += 1
                if event.key == pg.K_KP4:
                    self.enviro.sel_index -= 1
                self.enviro.sel_index = clamp(self.enviro.sel_index, 0, len(self.enviro.my_creatures)-1)
                if old_sel_index != self.enviro.sel_index:
                    self.enviro.selected = self.enviro.my_creatures[self.enviro.sel_index]
            elif event.key == pg.K_F1:
                if self.enviro.selected:
                    self.SaveCreature(self.enviro.selected)
            elif event.key == pg.K_F2:
                if self.enviro.selected:
                    self.LoadCreature(dt)
            elif event.key == pg.K_KP_PLUS:
                cfg["DELTA"] += 1
                cfg["DELTA"] = clamp(cfg['DELTA'], 1, 10)
                #print(f"{self.enviro.Time(1)}: TIME X " + str(cfg['DELTA']))
            elif event.key == pg.K_KP_MINUS:
                cfg["DELTA"] -= 1
                cfg["DELTA"] = clamp(cfg['DELTA'], 1, 10)
                #print(f"{self.enviro.Time(1)}: TIME X " + str(cfg['DELTA']))
            elif event.key == pg.K_l:
                self.enviro.show_lists = not self.enviro.show_lists
            elif event.key == pg.K_n:
                self.enviro.show_network = not self.enviro.show_network
            elif event.key == pg.K_i:
                self.enviro.show_input = not self.enviro.show_input
            elif event.key == pg.K_c:
                self.enviro.creature_info = not self.enviro.creature_info
            elif event.key == pg.K_END:
                colors = {"herb_fit": "yellowgreen", "pred_fit": "orange"}
                PlotData('Fitness', colors, {"herb_fit": self.enviro.stats['herb_fit'], "pred_fit": self.enviro.stats['pred_fit']}, self.project_name)
            elif event.key == pg.K_DELETE:
                colors = {"herbs": "yellowgreen", "preds": "orange", "all": "blue"}
                PlotData('Borns', colors, self.enviro.borns, self.project_name)
            elif event.key == pg.K_INSERT:
                colors = {"food": "yellowgreen", "size": "yellow", "speed": "blue", "power": "red", "mutations": "orange", "recombinations": "purple"}
                PlotData('Skills', colors, self.enviro.stats, self.project_name, ['fitness', 'herb_fit', 'pred_fit'])
            elif event.key == pg.K_v:
                if self.enviro.selected:
                    rect = Rect((self.enviro.selected.x-50, self.enviro.selected.y-50), (100, 100))
                    view = self.screen.subsurface(rect)
                    path_str = f"saves/{self.project_name}/view.png"
                    pg.image.save(view, path_str)
                    #print(f"{self.enviro.Time(1)}: {self.enviro.selected.name}'s view has been saved to png file")
            elif event.key == pg.K_g:
                if self.enviro.selected:
                    path_str = f"saves/{self.project_name}"
                    self.NetToSVG(self.enviro.selected.neuro, self.enviro.selected.name, path_str)
                    #print(f"{self.enviro.Time(1)}: {self.enviro.selected.name}'s brain has been saved to svg file")
            elif event.key == pg.K_UP:
                self.MoveScreen(0, -100)
            elif event.key == pg.K_DOWN:
                self.MoveScreen(0, 100)
            elif event.key == pg.K_LEFT:
                self.MoveScreen(-100, 0)
            elif event.key == pg.K_RIGHT:
                self.MoveScreen(100, 0)
            elif event.key == pg.K_w:
                self.MoveScreen(0, -10)
            elif event.key == pg.K_s:
                self.MoveScreen(0, 10)
            elif event.key == pg.K_a:
                self.MoveScreen(-10, 0)
            elif event.key == pg.K_d:
                self.MoveScreen(10, 0)