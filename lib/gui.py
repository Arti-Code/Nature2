import os
from os import listdir, scandir
import sys
import json
from shutil import copyfile
from collections import deque
from statistics import mean
import pygame
import pygame_gui
from copy import copy
from pygame import Rect
from pygame_gui import UIManager, PackageResource
from pygame_gui.elements import UITextBox, UIWindow, UIButton, UILabel, UITextEntryLine, UIPanel
from pygame_gui.core import UIFontDictionary
from lib.config import cfg, TITLE, SUBTITLE, AUTHOR
from lib.life import Life
from lib.creature import Creature
from lib.plant import Plant
from lib.meat import Meat


btn_w = 150
btn_h = 30
btn_h_xs = 15
space = 5
btn_s = 10

class NewSimWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):

        super().__init__(rect, manager=manager, window_display_title='New Simulation', object_id="#new_win", visible=True)
        self.manager = manager
        self.label = UILabel(Rect((50, 15), (200, 30)), text='Enter New Project Name', manager=manager, container=self, parent_element=self)
        self.edit = UITextEntryLine(Rect((50, 50), (200, 30)), manager=manager, container=self, parent_element=self)
        self.cancel = UIButton(Rect((50, 100), (75, 30)), text='Cancel', manager=manager, container=self, parent_element=self, object_id='#btn_cancel')
        self.accept = UIButton(Rect((175, 100), (75, 30)), text='Accept', manager=manager, container=self, parent_element=self, object_id='#btn_accept')

class SelectNet(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):

        super().__init__(Rect((400, 200), (300, 180)), manager=manager, window_display_title='Select Neural Network', object_id="#win_sel_net", visible=True)
        self.manager = manager
        self.label = UILabel(Rect((25, 20), (250, 18)), text='Enter Neural Network Name', manager=manager, container=self, parent_element=self)
        self.edit = UITextEntryLine(Rect((75, 60), (150, 18)), manager=manager, container=self, parent_element=self)
        self.cancel = UIButton(Rect((50, 100), (75, 30)), text='Cancel', manager=manager, container=self, parent_element=self, object_id='#btn_cancel')
        self.accept = UIButton(Rect((175, 100), (75, 30)), text='Accept', manager=manager, container=self, parent_element=self, object_id='#btn_accept')

class MapWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):

        super().__init__(Rect((400, 200), (300, 180)), manager=manager, window_display_title='Map Simulation', object_id="#map_win", visible=True)
        self.manager = manager
        self.label = UILabel(Rect((25, 20), (250, 18)), text='Enter Map Name', manager=manager, container=self, parent_element=self)
        self.edit = UITextEntryLine(Rect((75, 60), (150, 18)), manager=manager, container=self, parent_element=self)
        self.cancel = UIButton(Rect((50, 100), (75, 30)), text='Cancel', manager=manager, container=self, parent_element=self, object_id='#btn_cancel')
        self.accept = UIButton(Rect((175, 100), (75, 30)), text='Accept', manager=manager, container=self, parent_element=self, object_id='#btn_accept')

class MenuWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Main Menu', object_id="#menu_win", visible=True)
        self.manager = manager
        btn_list = [('Resume', '#btn_resume'), ('New Simulation', '#btn_sim'), ('Save Menu', '#save_menu'), ('Load Menu', '#btn_load'), ('Settings', '#btn_set'), ('Info', '#btn_info'), ('Quit', '#btn_quit')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s*(i)+btn_h*(i-1))), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class LoadWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Load Menu', object_id="#load_win", visible=True)
        self.manager = manager
        btn_list = [('Load Simulation', '#btn_load_sim'), ('Load Creature', '#btn_load_creature'), ('Back', '#btn_load_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s*(i)+btn_h*(i-1))+btn_h), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class DelBtn(UIButton):

    def __init__(self, rect: Rect, text: str, manager: UIManager, container, parent_element, object_id: str, sim_to_kill: str):
        super().__init__(rect, text, manager, container, parent_element=parent_element, object_id=object_id)
        self.sim_to_kill = sim_to_kill

class DelSpecBtn(UIButton):

    def __init__(self, rect: Rect, text: str, manager: UIManager, container, parent_element, object_id: str, spec_to_kill: str):
        super().__init__(rect, text, manager, container, parent_element=parent_element, object_id=object_id)
        self.spec_to_kill = spec_to_kill

class LoadBtn(UIButton):

    def __init__(self, rect: Rect, text: str, manager: UIManager, container, parent_element, object_id: str, obj_to_load: str):
        super().__init__(rect, text, manager, container, parent_element=parent_element, object_id=object_id)
        self.obj_to_load = obj_to_load
class LoadSimWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, simulations: list):
        super().__init__(rect, manager=manager, window_display_title='Load Simulation', object_id="#load_sim_win", visible=True)
        self.manager = manager
        buttons = []
        i = 1
        for sim in simulations:
            btn = UIButton(Rect((40, (btn_s+btn_h)*i), (btn_w, btn_h)), text=sim, manager=self.manager, container=self, parent_element=self, object_id='#btn_load_sim')
            del_btn = DelBtn(Rect((200, (btn_s+btn_h)*i), (btn_h, btn_h)), 'X', manager=manager, container=self, parent_element=self, object_id='#btn_del', sim_to_kill=sim)
            buttons.append((btn, del_btn))
            i += 1
        btn = UIButton(Rect((40, (btn_s+btn_h)*i), (btn_w, btn_h)), text='Back', manager=self.manager, container=self, parent_element=self, object_id='#btn_load_sim_back')

class LoadCreatureWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, creature_names: list):
        super().__init__(rect, manager=manager, window_display_title='Load Creature', object_id="#load_creature_win", resizable=True, visible=True)
        self.manager = manager
        creatures = self.read_creature_list(creature_names=creature_names)
        buttons = []
        i = 0
        for c in creatures:
            text = f"{c[0]}   [G:{c[1]}]  [P:{c[2]}]  [F:{c[3]}]  [M:{c[4]}]  [S:{c[5]}]"
            btn = LoadBtn(Rect((5, (space+btn_h_xs)*i+5), (btn_h_xs, btn_h_xs)), text="", manager=self.manager, container=self, parent_element=self, object_id='#btn_load_creature', obj_to_load=c[0])
            lab = UILabel(Rect((25, (space+btn_h_xs)*i+5), (btn_w+100, btn_h_xs)), text=text, manager=self.manager, container=self, parent_element=self, object_id='#lab_creature_to_load')
            btn = DelSpecBtn(Rect((280, (space+btn_h_xs)*i+5), (btn_h_xs, btn_h_xs)), text="", manager=self.manager, container=self, parent_element=self, object_id='#btn_del_spec', spec_to_kill=c[0])
            buttons.append((lab, btn))
            i += 1
        #btn = UIButton(Rect((50, (space+btn_h_xs)*i+10), (btn_w, btn_h)), text='Back', manager=self.manager, container=self, parent_element=self, object_id='#load_creature_back')

    def read_creature_list(self, creature_names: list) -> list:
        creatures = []
        for f_name in creature_names:
            f = open("saves/creatures/"+f_name, "r")
            json_creature = f.read()
            f.close()
            creature = json.loads(json_creature)
            creatures.append((creature['name'], creature['gen'], creature['power'], creature['food'], creature['speed'], int(creature['size'])))
        return creatures

class RankWindow(UIWindow):

    def __init__(self, owner, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Ranking', object_id="#rank_win", resizable=True, visible=True)
        self.owner = owner
        self.manager = manager
        self.labels = []
        for i in range(cfg.RANK_SIZE):
            text = '.'
            num = UILabel(Rect((1, 11*i+1), (14, 10)), text=text, manager=manager, container=self, parent_element=self, object_id='#rank_label')
            spec = UILabel(Rect((15, 11*i+1), (38, 10)), text=text, manager=manager, container=self, parent_element=self, object_id='#rank_label')
            gen = UILabel(Rect((55, 11*i+1), (28, 10)), text=text, manager=manager, container=self, parent_element=self, object_id='#rank_label')
            eat = UILabel(Rect((85, 11*i+1), (15, 10)), text=text, manager=manager, container=self, parent_element=self, object_id='#rank_label')
            fit = UILabel(Rect((101, 11*i+1), (39, 10)), text=text, manager=manager, container=self, parent_element=self, object_id='#rank_label')
            self.labels.append([num, spec, gen, eat, fit])

    def Update(self, ranking1: list, ranking2: list):
        rank_count1 = len(ranking1)
        for i in range(rank_count1):
            self.labels[i][0].set_text(str(i+1)+'.')
            self.labels[i][1].set_text(ranking1[i]['name'])
            self.labels[i][2].set_text('G' + str(ranking1[i]['gen']))
            self.labels[i][3].set_text('E' + str(ranking1[i]['food']))
            #self.labels[i][4].set_text('F' + str(round(ranking1[i]['fitness']/1000, 2)) + "k")
            self.labels[i][4].set_text('F' + str(round(ranking1[i]['fitness'])))
        
class InfoWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, text: str, title: str=''):
        super().__init__(rect, manager=manager, window_display_title=title, object_id="#info_win", visible=True)
        self.manager = manager
        btn = UIButton(Rect((round((self.rect.width/2)-(btn_w/2)), 60), (btn_w, btn_h)), text='OK', manager=self.manager, container=self, parent_element=self, object_id='#btn_info')
        msg = UILabel(Rect((10, 15), (self.rect.width-10, 40)), text=text, manager=manager, container=self, parent_element=self, object_id='txt_msg')

class CreditsWindow(UIWindow):

    def __init__(self, owner: object, manager: UIManager, rect: Rect, title: str, subtitle: str, author: str, bar_text: str=''):
        super().__init__(rect, manager=manager, window_display_title=bar_text, object_id="#credits_win", visible=True)
        self.manager = manager
        btn_w = 60; btn_h = 20
        btn = UIButton(Rect((round((self.rect.width/2)-(btn_w/2)), 55), (btn_w, btn_h)), text='CLOSE', manager=self.manager, container=self, parent_element=self, object_id='#btn_credits_close')
        lab_title = UILabel(Rect((10, 5), (self.rect.width-10, 20)), text=title, manager=manager, container=self, parent_element=self, object_id='#txt_title')
        lab_subtitle = UILabel(Rect((10, 25), (self.rect.width-10, 15)), text=subtitle, manager=manager, container=self, parent_element=self, object_id='#txt_subtitle')
        lab_author = UILabel(Rect((10, 40), (self.rect.width-10, 15)), text=author, manager=manager, container=self, parent_element=self, object_id='#txt_author')

class EnviroWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        super().__init__(rect, manager=manager, window_display_title='Enviroment Info', object_id="#enviro_win", visible=True)
        self.manager = manager
        i=0
        self.labs = {}
        for key, val in data.items():
            lab1 = UILabel(Rect((5, 15*i+5), (75, 15)), text=f"{key}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_key'+str(i))
            lab2 = UILabel(Rect((80, 15*i+5), (self.rect.width/2-5, 15)), text=f"{val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_val'+str(i))
            i+=1
            self.labs[key] = (lab1, lab2)
        self.btn_close = UIButton(Rect((rect.width/2-btn_w/2, (15+15*i)), (btn_w, btn_h)), text='Close', manager=self.manager, container=self, parent_element=self, object_id='#btn_quit')
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        if self.refresh <= 0:
            self.refresh = 0.1
            data = data
            for key, val in data.items():
                self.labs[key][0].set_text(f"{key}:")
                self.labs[key][1].set_text(f"{val}")

class CreatureWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        super().__init__(rect=rect, manager=manager, window_display_title=data['SPECIE'] + ' ['+data['G']+']', object_id="#creature_win", resizable=True, visible=True)
        grid: dict[tuple]={
                "D": (0, 0, 2), "O": (0, 2, 2), 
                "M": (1, 0, 2), "V": (1, 2, 2), 
                "P": (2, 0, 2), "X": (2, 2, 2), 
                "F": (3, 0, 2), "R": (3, 2, 2),
                "B": (4, 0, 2), "K": (4, 2, 2), 
                "L": (5, 0, 2), "S": (5, 2, 2),
                "ENG": (6, 0, 4)
        } 
        self.manager = manager
        self.labs = {}
        i = 0
        for key, val in data.items():
            if key in [*grid.keys()]:
                (row, col, siz) = grid[key]
                lab1 = UILabel(Rect((20*col+2, 10*row+2), (siz*20, 10)), text=f"{key}:{val}", manager=self.manager, container=self, parent_element=self, object_id='#lab_creature_win')
                self.labs[key] = lab1
                i = max(i, row+1)
        btn_w = 80; btn_h = 20
        self.btn_ancestors = UIButton(Rect((rect.width/2-btn_w/2, (5+10*i)), (btn_w, btn_h)), text='HISTORY', manager=self.manager, container=self, parent_element=self, object_id="#btn_ancestors")
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        self.set_display_title(data['SPECIE'] +' ['+data['G']+']')
        if self.refresh <= 0:
            self.refresh = 1
            data = data
            for key, val in data.items():
                if key in [*self.labs.keys()]:
                    self.labs[key].set_text(f"{key}:{val}")

class TestWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, bar_text: str=''):
        super().__init__(rect, manager=manager, window_display_title=bar_text, object_id="#test_win", visible=True)
        self.manager = manager

class CreatureAdvanceWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        grid: dict[tuple]={
            "B": (0, 0, 2),
            "M": (0, 2, 2),
            "N": (1, 0, 2),
            "O": (1, 2, 2),
            "T": (2, 0, 4)
        } 
        energy_data = data["C"]
        super().__init__(rect, manager=manager, window_display_title=f"{data['SPECIE']}", object_id="#creature_advance_win", resizable=True, visible=True)
        self.manager = manager
        self.labs = {}
        for key, val in energy_data.items():
            if key in [*grid.keys()]:
                (row, col, siz) = grid[key]
                lab1 = UILabel(Rect((20*col+2, 10*row+5), (siz*25, 15)), text=f"{key}: {val}", manager=self.manager, container=self, parent_element=self, object_id='#lab_creature_win')
                self.labs[key] = lab1
        #btn_w = 80; btn_h = 20
        #self.btn_ancestors = UIButton(Rect((rect.width/2-btn_w/2, (5+15*i)), (btn_w, btn_h)), text='ANCESTORS', manager=self.manager, container=self, parent_element=self, object_id="#btn_ancestors")
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        self.set_display_title(data['SPECIE'])
        if self.refresh <= 0:
            self.refresh = 1
            eng_data = data["C"]
            for key, val in eng_data.items():
                if key in [*self.labs.keys()]:
                    self.labs[key].set_text(f"{key}: {val}")

class AncestorsWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, history: list):
        super().__init__(rect, manager=manager, window_display_title='Ancestors', object_id="#genealogy_win", visible=True)
        self.manager = manager
        i=0
        self.labels = []
        for (specie, gen, time) in history:
            lab = UILabel(Rect((5, 10*i+2), (rect.width-10, 10)), text=f"T({time}) {specie} G({gen})", manager=self.manager, container=self, parent_element=self, object_id='lab_ancestor'+str(i))
            self.labels.append(lab)
            i += 1


class CreatureHistoryWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, parents: list, dT: float):
        super().__init__(rect, manager=manager, window_display_title='Creature Genealogy', object_id="#history_win", visible=True)
        self.manager = manager
        i=0
        self.labs = {}
        for (time, specie) in parents:
            lab = UILabel(Rect((5, 15*i+5), (70, 15)), text=f"[{time}] {specie} >>>>", manager=self.manager, container=self, parent_element=self, object_id='lab_specie_'+str(time))
            self.labs.append(lab)
        self.refresh = 0
        self.update(parents, dT)

    def update(self, parents: list, dT: float):
        self.refresh -= dT
        if self.refresh <= 0:
            self.refresh = 1
            parents = parents
            i = 0
            for (time, specie) in parents:
                self.lab[i].set_text(f"[{time}] {specie} >>>>")

class SettingsWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Settings', object_id="#set_win", visible=True)
        self.manager = manager
        btn_list = [('Reload Settings', '#btn_rel_set'), ('Back', '#btn_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s+btn_h)*i), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class InfoMenuWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Info Menu', object_id="#info_menu", visible=True)
        self.manager = manager
        btn_list = [('Creature Info', '#creature_win'), ('Special Info', '#creature_advance_win'), ('Enviroment Info', '#enviro'), ('Ranking', '#rank'), ('Credits', '#credits'), ('Back', '#info_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s*i+btn_h*(i-1))), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class SaveMenuWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Save Menu', object_id="#save_menu", visible=True)
        self.manager = manager
        btn_list = [('Save Progress', '#save_progress'), ('Save Creature', '#save_creature'), ('Back', '#save_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s+btn_h)*i), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class CustomGUIWin(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Settings', object_id="#set_win", visible=True)
        self.manager = manager
        btn_list = [('Basic Data', '#btn_basic_data'), ('Back', '#btn_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s+btn_h)*i), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class GUI():

    def __init__(self, owner: object, view: tuple, edytor=False):
        self.view = view
        self.owner = owner
        self.edytor = edytor
        self.cx = round(cfg.SCREEN[0]/2)
        self.cy = round(cfg.SCREEN[1]/2)
        self.ui_mgr = UIManager(window_resolution=view, theme_path='res/themes/blue.json')
        self.ui_mgr.add_font_paths('fira.ttf', 'res/fonts/fira.ttf')
        self.ui_mgr.add_font_paths('fira', 'res/fonts/fira.ttf')
        self.buttons = []
        self.title = None
        self.subtitle = None
        self.world = None
        self.btn_menu = None
        self.main_menu = None
        self.new_sim = None
        self.map_sim = None
        self.load_menu = None
        self.info_win = None
        self.set_win = None
        self.info_menu = None
        self.save_menu = None
        self.enviro_win = None
        self.creature_win = None
        self.creature_advance_win = None
        self.rank_win = None
        self.credits_win = None
        self.history_win = None
        self.ancestors_win = None
        self.test_win = None
        self.rebuild_ui(self.view)

    def rebuild_ui(self, new_size: tuple):         
        self.ui_mgr.set_window_resolution(new_size)
        self.ui_mgr.clear_and_reset()
        self.size = new_size
        self.create_title(new_size)
        btn_pos = Rect((round(cfg.SCREEN[0]-57), 2), (55, 55))
        self.create_menu_btn(btn_pos)

    def get_saved_creatures(self) -> list:
        creatures = []
        crs = scandir("saves/creatures")
        for c in crs:
            if c.is_file():
                creatures.append(c.name)
        crs.close()
        return creatures

    def get_all_simulations(self) -> list:
        projects = []
        dirs = scandir("saves")
        for d in dirs:
            if d.is_dir():
                if d.name == "creatures":
                    continue
                projects.append(d.name)
        dirs.close()
        return projects

    def get_all_simulations2(self) -> list:
        projects = []
        f = open("saves/projects.json", "r")
        json_sim = f.read()
        f.close()
        sims = json.loads(json_sim)
        for sim in sims['projects']:
            projects.append(sim)
        return projects

    def create_menu_btn(self, rect: Rect):
        self.btn_menu = UIButton(rect, 'MENU', self.ui_mgr, object_id='#btn_menu')

    def create_test(self):
        self.test_win = TestWindow(manager=self.ui_mgr, rect=Rect((5, 5), (75, 25)), bar_text='Test')

    def create_custom_btn(self, rect: Rect, title: str, obj_id: str):
        btn = UIButton(relative_rect=rect, text=title, manager=self.ui_mgr, object_id=obj_id)
        return btn

    def load_creature(self, creature_name: str):
        self.owner.load_creature(name=creature_name)

    def delete_creature(self, creature_name: str):
        self.owner.delete_creature(name=creature_name)

    def create_main_menu(self):
        w = 250
        h = 350
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.main_menu = MenuWindow(manager=self.ui_mgr, rect=pos)

    def create_settings(self):
        w = 250
        h = 200
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.set_win = SettingsWindow(manager=self.ui_mgr, rect=pos)

    def create_info_menu(self):
        w = 250
        h = 300
        pos = Rect((self.cx-w/2, self.cy-h), (w, h))
        self.info_menu = InfoMenuWindow(manager=self.ui_mgr, rect=pos)

    def save_creature(self, selected: Life):
        if isinstance(selected, Creature):
            self.owner.save_creature(selected)

    def create_save_menu(self):
        w = 250
        h = 250
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.save_menu = SaveMenuWindow(manager=self.ui_mgr, rect=pos)

    def create_new_sim_win(self):
        w = 300
        h = 150
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h+25))
        self.main_menu.kill()
        self.new_sim = NewSimWindow(manager=self.ui_mgr, rect=pos)

    def create_new_sim(self):
        new_name = self.new_sim.edit.get_text()
        self.owner.enviro.project_name = new_name
        if not self.new_project_name(new_name):
            return
        cfg.load_from_file2('saves/' + new_name + '/config.json')
        self.create_title(cfg.SCREEN)
        self.owner.enviro.create_enviro()
        self.create_info_win(text='Project created with name: ' + new_name, title=new_name)

    def create_load_menu(self):
        w = 250
        h = 200
        pos = Rect((self.cx-w/2, self.cy-h+100), (w, h))
        self.load_menu = LoadWindow(manager=self.ui_mgr, rect=pos)

    def create_load_sim_menu(self):
        w = 250
        #h = 400
        simulations = self.get_all_simulations()
        sim_num = len(simulations)
        h = 75 + (25 * sim_num)
        pos = Rect((self.cx-w/2, self.cy-h+100), (w, h+200))
        self.load_sim_menu = LoadSimWindow(manager=self.ui_mgr, rect=pos, simulations=simulations)

    def create_load_creature_win(self):
        w = 300
        creatures = self.get_saved_creatures()
        cr_num = len(creatures)
        h = 10 + (20 * cr_num)
        pos = Rect((10+self.cx-w/2, 25), (w, h+10))
        self.load_creature_win = LoadCreatureWindow(manager=self.ui_mgr, rect=pos, creature_names=creatures)

    def create_info_win(self, text: str, title: str):
        w = 250
        h = 120
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.info_win = InfoWindow(manager=self.ui_mgr, rect=pos, text=text, title=title)

    def create_credits_win(self, title: str, subtitle: str, author: str, bar_text: str):
        w = 250
        h = 100
        pos = Rect((self.cx-w/2, self.cy), (w, h))
        self.credits_win = CreditsWindow(owner=self.owner, manager=self.ui_mgr, rect=pos, title=title, subtitle=subtitle, author=author, bar_text=bar_text)

    def create_rank_win(self):
        w = 140
        h = cfg.RANK_SIZE * 11 + 25
        pos = Rect((self.cx*2-(w+10), 25), (w, h))
        self.rank_win = RankWindow(self, manager=self.ui_mgr, rect=pos)

    def update_ranking(self, ranking1: list, ranking2: list) -> dict:
        return [ranking1, ranking2]

    def create_title(self, scr_size: tuple):
        w = 350
        h = 25
        h2 = 20
        title_rect = Rect((round(cfg.SCREEN[0]/2-w/2), (10)), (w, h))
        world_rect = Rect((round(cfg.SCREEN[0]/2-w/2), (35)), (w, h2))
        self.title = UILabel(relative_rect=title_rect, text=TITLE, manager=self.ui_mgr, object_id='#lab_title')
        if self.owner.enviro.project_name != None:
            self.world = UILabel(relative_rect=world_rect, text=self.owner.enviro.project_name, manager=self.ui_mgr, object_id='#lab_world')

    def kill_title(self):
        self.title.kill()
        #self.subtitle.kill()
        if self.world:
            self.world.kill()

    def create_enviro_win(self, dT: float):
        data = {}
        data['dT'] = ''
        data['TIME'] = ''
        data['CREATURES'] = 'H:'+str(self.owner.enviro.herbivores)+'|C:'+str(self.owner.enviro.carnivores)
        data['PLANTS'] = str(len(self.owner.enviro.plant_list))
        data['NEURO'] = ''
        data['PHYSIC'] = ''
        data['FOLLOW'] = str(self.owner.enviro.follow)
        self.enviro_win = EnviroWindow(manager=self.ui_mgr, rect=Rect((0, 0), (160, 140)), data=data, dT=dT)

    def create_creature_win(self, dT: float):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.update_creature_win()
            w = 110; h = 140
            pos = Rect((self.cx*2-(w+10), 25), (w, h))
            self.creature_win = CreatureWindow(manager=self.ui_mgr, rect=pos, data=data, dT=dT)

    def create_creature_advance_win(self, dT: float):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.update_creature_win()
            self.creature_advance_win = CreatureAdvanceWindow(manager=self.ui_mgr, rect=Rect((115, 5), (110, 60)), data=data, dT=dT)

    def create_ancestors_win(self, dT: float):
        if self.ancestors_win:
            self.ancestors_win.kill()
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            count = len(data)
            height = 2 + 15 * count
            self.ancestors_win = AncestorsWindow(manager=self.ui_mgr, rect=Rect((500, 0), (150, height)), history=data)

    def create_history_win(self, dT: float):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            self.history_win = CreatureHistoryWindow(manager=self.ui_mgr, rect=Rect((200, 200), (150, 400)), parents=data, dT=dT)

    def update_creature_history(self, dT):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            self.history_win.Update(data, dT)

    def update_creature_win(self) -> dict:
        selected = self.owner.enviro.selected
        if not isinstance(selected, Creature):
            data = {}
            data['SPECIE'] = ''
            data['G'] = ''
            data['ENG'] = ''
            data['D'] = ''
            data['P'] = ''
            data['M'] = ''
            data['V'] = ''
            data['O'] = ''
            data['X'] = ''
            data['B'] = ''
            data['K'] = ''
            data['F'] = ''
            data["L"] = ''
            data["R"] = ''
            data['S'] = ''
            data['C'] = {}
            if isinstance(selected, Plant):
                data['SPECIE'] = 'PLANT'
                data['L'] = str(round(selected.life_time))
                data['ENG'] = str(round(selected.energy))
                data['O'] = str(round(selected.shape.radius))
                #data['S'] = str(len(selected.plants_in_area))
            elif isinstance(selected, Meat):
                data['L'] = str(round(selected.life_time))
                data['SPECIE'] = 'MEAT'
                data['ENG'] = str(round(selected.energy))
                data['O'] = str(round(selected.radius))
            return data
        data = {}
        data['SPECIE'] = selected.name
        data['G'] = str(selected.generation)
        data['ENG'] = str(round(selected.energy))+'/'+str(round(selected.max_energy))
        data['D'] = str(selected.food)
        data['P'] = str(selected.power)
        data['M'] = str(selected.speed)
        data['V'] = str(selected.eyes)
        data['O'] = str(selected.size)
        data['X'] = f"{selected.mutations}"
        data['B'] = str(selected.childs)
        data['K'] = str(selected.kills)
        data['F'] = str(round(selected.fitness))
        data["L"] = str(round(selected.life_time))
        data["R"] = str(round(selected.reproduction_time))
        states = []
        if selected.hidding:
            states.append('H')
        if selected.attacking:
            states.append('A')
        if selected.running:
            states.append('R')
        if selected.on_water:
            states.append('W')
        if selected.eating:
            states.append('E')
        if selected.pain:
            states.append('T')
        if selected.collide_creature:
            states.append('C')
        if selected.collide_meat:
            states.append('M')
        if selected.collide_plant:
            states.append('P')
        if len(states) > 0:
            data['S'] = ''
        else:
            data['S'] = ''
        i = 0
        for state in states:
            i += 1
            data['S'] += state
            if i < len(states):
                data['S'] += '|'
        total_eng_cost = round(selected.eng_lost['basic']+selected.eng_lost['move']+selected.eng_lost['neuro']+selected.eng_lost['other'], 1)
        data['C'] = {
                "B": round(selected.eng_lost['basic'], 1),
                "M": round(selected.eng_lost['move'], 1),
                "N": round(selected.eng_lost['neuro'], 1),
                "O": round(selected.eng_lost['other'], 1),
                "T": total_eng_cost
        }
        return data

    def select_map(self):
        w = 300
        h = 100
        scr_w = self.owner.w
        scr_h = self.owner.h
        pos = Rect((scr_w/2-w/2, scr_h/2-h/2), (w, h))
        self.main_menu.kill()
        self.map_sim = MapWindow(manager=self.ui_mgr, rect=pos)

    def delete_project(self, sim_name: str):
        if sim_name != self.owner.enviro.project_name:
            self.owner.delete_project(sim_name)

    def update_enviroment(self, dT: float) -> dict:
        data = {}
        data['dT'] = str(round(dT, 3)) + 's'
        data['TIME'] = str(self.owner.enviro.cycles*6000 + round(self.owner.enviro.time)) + 's'
        data['CREATURES'] = 'H:'+str(self.owner.enviro.herbivores)+'|C:'+str(self.owner.enviro.carnivores)
        data['PLANTS'] = str(len(self.owner.enviro.plant_list))
        data['NEURO'] = str(round(self.owner.enviro.neuro_avg_time*1000, 1)) + 'ms'
        data['PHYSIC'] = str(round(self.owner.enviro.physics_avg_time*1000, 1)) + 'ms'
        data['FOLLOW'] = str(self.owner.enviro.follow)
        return data

    def process_event(self, event, dt: float)->bool:
        self.ui_mgr.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                #   >>> MAIN MENU <<<
                if event.ui_object_id == '#btn_menu':
                    self.create_main_menu()
                elif event.ui_object_id == '#menu_win.#btn_resume':
                    self.main_menu.kill()
                elif event.ui_object_id == '#menu_win.#btn_sim':
                    self.main_menu.kill()
                    self.create_new_sim_win()
                elif event.ui_object_id == '#menu_win.#btn_map':
                    self.main_menu.kill()
                    self.select_map()
                elif event.ui_object_id == '#menu_win.#save_menu':
                    self.main_menu.kill()
                    self.create_save_menu()
                elif event.ui_object_id == '#menu_win.#btn_info':
                    self.main_menu.kill()
                    self.create_info_menu()
                elif event.ui_object_id == '#menu_win.#btn_load':
                    self.main_menu.kill()
                    self.create_load_menu()
                elif event.ui_object_id == '#menu_win.#btn_quit':
                    pygame.quit()
                    sys.exit(0)
                
                #   >>> NEW SIM <<<
                elif event.ui_object_id == '#new_win.#btn_cancel':
                    self.new_sim.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#new_win.#btn_accept':
                    self.create_new_sim()
                    self.new_sim.kill()
                    
                #   >>> SAVE MENU <<<
                elif event.ui_object_id == '#save_menu.#save_progress':
                    self.owner.save_project()
                    self.save_menu.kill()
                elif event.ui_object_id == '#save_menu.#save_creature':
                    self.save_menu.kill()
                    self.save_creature(selected=self.owner.enviro.selected)
                elif event.ui_object_id == '#save_menu.#save_back':
                    self.save_menu.kill()
                    self.create_main_menu()
                
                #   >>> SETTINGS WIN <<<
                elif event.ui_object_id == '#menu_win.#btn_set':
                    self.main_menu.kill()
                    self.create_settings()
                elif event.ui_object_id == '#set_win.#btn_back':
                    self.set_win.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#set_win.#btn_rel_set':
                    self.reload_config()

                #   >>> LOAD MENU <<<
                elif event.ui_object_id == '#load_win.#btn_load_back':
                    self.load_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#load_win.#btn_load_sim':
                    self.load_menu.kill()
                    self.create_load_sim_menu()
                elif event.ui_object_id == '#load_win.#btn_load_creature':
                    self.load_menu.kill()
                    self.create_load_creature_win()
                elif isinstance(event.ui_element, DelBtn):
                    self.delete_project(event.ui_element.sim_to_kill)
                    self.load_sim_menu.kill()
                    self.create_load_sim_menu()
                elif event.ui_object_id == '#load_sim_win.#btn_load_sim_back':
                    self.load_sim_menu.kill()
                    self.create_load_menu()
                elif event.ui_object_id[0: 27] == '#load_sim_win.#btn_load_sim':
                    project_name = event.ui_element.text
                    self.owner.enviro.project_name = project_name
                    self.owner.load_last(project_name)
                    self.load_sim_menu.kill()   
                    self.kill_title()
                    self.create_title(cfg.SCREEN) 
                    self.create_info_win(text=f"Project {project_name.upper()} has been loaded", title='Load Simulation')
                #   >>> INFO MENU <<<
                elif event.ui_object_id == '#info_win.#btn_info':
                    self.info_win.kill()
                elif event.ui_object_id == '#info_menu.#enviro':
                    #self.info_menu.kill()
                    self.create_enviro_win(dt)
                elif event.ui_object_id == '#info_menu.#creature_win':
                    #self.info_menu.kill()
                    self.create_creature_win(dt)
                elif event.ui_object_id == '#info_menu.#creature_advance_win':
                    #self.info_menu.kill()
                    self.create_creature_advance_win(dt)
                elif event.ui_object_id == '#creature_win.#btn_ancestors':
                    self.create_ancestors_win(dt)
                elif event.ui_object_id == '#info_menu.#rank':
                    #self.info_menu.kill()
                    self.create_rank_win()
                elif event.ui_object_id == '#info_menu.#credits':
                    #self.info_menu.kill()
                    self.create_credits_win(title=TITLE, subtitle=SUBTITLE, author=AUTHOR, bar_text=TITLE)
                elif event.ui_object_id == '#info_menu.#info_back':
                    self.info_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#rank_win.#btn_quit':
                    self.rank_win.kill()
                elif event.ui_object_id == '#enviro_win.#btn_quit':
                    self.enviro_win.kill()
                elif event.ui_object_id == '#credits_win.#btn_credits_close':
                    self.credits_win.kill()
                #   >>> LOAD CREATURE WINDOW <<<
                elif event.ui_object_id == '#load_creature_win.#btn_load_creature':
                    creature_name = event.ui_element.obj_to_load
                    self.load_creature(creature_name=creature_name)
                elif event.ui_object_id == '#load_creature_win.#btn_del_spec':
                    spec = event.ui_element.spec_to_kill
                    self.load_creature_win.kill()
                    self.delete_creature(spec)
                    self.create_load_creature_win()
            return True
        else:
            return False

    def reload_config(self):
        self.set_win.kill()
        cfg.load_from_file2('saves/' + self.owner.enviro.project_name + '/config.json')

    def update(self, dT: float, ranking1: list, ranking2: list):
        data: dict = {}
        self.ui_mgr.update(dT)
        if self.enviro_win:
            data = self.update_enviroment(dT)
            self.enviro_win.Update(data, dT)
        if self.rank_win:
            data = self.update_ranking(ranking1, ranking2)
            self.rank_win.Update(ranking1, ranking2)
        if self.creature_win and self.owner.enviro.selected:
            data = self.update_creature_win()
            self.creature_win.Update(data, dT)
        if self.creature_advance_win and self.owner.enviro.selected:
            data = self.update_creature_win()
            self.creature_advance_win.Update(data, dT)
        if self.history_win and self.owner.enviro.selected:
            self.update_creature_history(dT=dT)

    def draw_ui(self, screen):
        self.ui_mgr.draw_ui(screen)

    def new_project_name(self, name: str):
        projects_list = self.get_all_simulations()
        if name in projects_list:
            return False
        try:
            os.mkdir('saves/' + name)
            copyfile('config.json', 'saves/' + name + '/config.json')
        except FileExistsError:
            pass
        finally:
            return True