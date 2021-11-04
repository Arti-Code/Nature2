import os
import sys
import json
from collections import deque
from statistics import mean
import pygame
import pygame_gui
from copy import copy
from pygame import Rect
from pygame_gui import UIManager, PackageResource
from pygame_gui.elements import UITextBox, UIWindow, UIButton, UILabel, UITextEntryLine, UIPanel
from lib.config import cfg, TITLE, SUBTITLE, AUTHOR
from lib.life import Life
from lib.creature import Creature


btn_w = 150
btn_h = 30
btn_s = 10

class NewSimWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):

        super().__init__(rect, manager=manager, window_display_title='New Simulation', object_id="#new_win", visible=True)
        self.manager = manager
        self.label = UILabel(Rect((50, 15), (200, 15)), text='Enter New Project Name', manager=manager, container=self, parent_element=self)
        self.edit = UITextEntryLine(Rect((50, 50), (200, 20)), manager=manager, container=self, parent_element=self)
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
        btn_list = [('Resume', '#btn_resume'), ('New Simulation', '#btn_sim'), ('Select Terrain', '#btn_map'), ('Save Simulation', '#save_menu'), ('Load Simulation', '#btn_load'), ('Settings', '#btn_set'), ('Info', '#btn_info'), ('Quit', '#btn_quit')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s*(i)+btn_h*(i-1))), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class DelBtn(UIButton):

    def __init__(self, rect: Rect, text: str, manager: UIManager, container, parent_element, object_id: str, destroy_id: str):
        super().__init__(rect, text, manager, container, parent_element=parent_element, object_id=object_id)
        self.destroy_id = destroy_id

class LoadWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Load Menu', object_id="#load_win", visible=True)
        self.manager = manager
        simulations = self.GetAllSim()
        buttons = []
        i = 1
        for sim in simulations:
            btn = UIButton(Rect((60, (btn_s+btn_h)*i), (btn_w, btn_h)), text=sim, manager=self.manager, container=self, parent_element=self, object_id='#btn_load')
            del_btn = DelBtn(Rect((220, (btn_s+btn_h)*i), (btn_h, btn_h)), 'X', manager=manager, container=self, parent_element=self, object_id='#btn_del_', destroy_id=sim)
            buttons.append((btn, del_btn))
            i += 1
        btn = UIButton(Rect((75, (btn_s+btn_h)*i), (btn_w, btn_h)), text='Back', manager=self.manager, container=self, parent_element=self, object_id='#load_back')

    def GetAllSim(self):
            f = open("saves/projects.json", "r")
            projects_list = f.read()
            f.close()
            projects = json.loads(projects_list)
            return projects["projects"]

class RankWindow(UIWindow):

    def __init__(self, owner, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Ranking', object_id="#rank_win", visible=True)
        self.owner = owner
        self.manager = manager
        self.labels = []
        lbl_w = 305
        for i in range(cfg.RANK_SIZE*2):
            text = '.'
            num = UILabel(Rect((2, 15*i+5), (13, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_position_'+str(i))
            spec = UILabel(Rect((5+10, 15*i+5), (60, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_specie_'+str(i))
            gen = UILabel(Rect((5+70, 15*i+5), (55, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_generation_'+str(i))
            pwr = UILabel(Rect((5+125, 15*i+5), (45, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_power_'+str(i))
            eat = UILabel(Rect((5+170, 15*i+5), (45, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_eat_'+str(i))
            fit = UILabel(Rect((5+215, 15*i+5), (70, 15)), text=text, manager=manager, container=self, parent_element=self, object_id='rank_fitness_'+str(i))
            self.labels.append([num, spec, gen, pwr, eat, fit])
        #self.btn_close = UIButton(Rect((round((rect.width/2)-(btn_w/2)), (15*i+25)), (btn_w, btn_h)), text='Close', manager=self.manager, container=self, parent_element=self, object_id='#btn_quit')

    def Update(self, ranking1: list, ranking2: list):
        rank_count1 = len(ranking1)
        for i in range(rank_count1):
            self.labels[i][0].set_text(str(i)+'.')
            self.labels[i][1].set_text(ranking1[i]['name'])
            self.labels[i][2].set_text('GEN ' + str(ranking1[i]['gen']))
            self.labels[i][3].set_text('PWR ' + str(ranking1[i]['power']))
            self.labels[i][4].set_text('EAT ' + str(ranking1[i]['food']))
            self.labels[i][5].set_text('FIT ' + str(round(ranking1[i]['fitness'])))
        rank_count2 = len(ranking2)
        for i in range(rank_count2):
            j = i + rank_count1
            self.labels[j][0].set_text(str(i)+'.')
            self.labels[j][1].set_text(ranking2[i]['name'])
            self.labels[j][2].set_text('GEN ' + str(ranking2[i]['gen']))
            self.labels[j][3].set_text('PWR ' + str(ranking2[i]['power']))
            self.labels[j][4].set_text('EAT ' + str(ranking2[i]['food']))
            self.labels[j][5].set_text('FIT ' + str(round(ranking2[i]['fitness'])))

            #text = str(i) + '. ' + ranking[i]['name'] + ' \t GEN: ' + str(ranking[i]['gen']) + ' \t POW: ' + str(ranking[i]['power']) + ' \t MEAT|VEGE: ' + str(ranking[i]['meat']) + '|' + str(ranking[i]['vege']) + ' \t FIT: ' + str(round(ranking[i]['fitness']))
            #lab.set_text(text)

class InfoWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, text: str, title: str=''):
        super().__init__(rect, manager=manager, window_display_title=title, object_id="#info_win", visible=True)
        self.manager = manager
        btn = UIButton(Rect((round((self.rect.width/2)-(btn_w/2)), 60), (btn_w, btn_h)), text='Accept', manager=self.manager, container=self, parent_element=self, object_id='#btn_info')
        msg = UILabel(Rect((10, 15), (self.rect.width-10, 40)), text=text, manager=manager, container=self, parent_element=self, object_id='txt_msg')

class CreditsWindow(UIWindow):

    def __init__(self, owner: object, manager: UIManager, rect: Rect, title: str, subtitle: str, author: str, bar_text: str=''):
        super().__init__(rect, manager=manager, window_display_title=bar_text, object_id="#credits_win", visible=True)
        self.manager = manager
        btn = UIButton(Rect((round((self.rect.width/2)-(btn_w/2)), 80), (btn_w, btn_h)), text='Close', manager=self.manager, container=self, parent_element=self, object_id='#btn_close')
        lab_title = UILabel(Rect((10, 5), (self.rect.width-10, 30)), text=title, manager=manager, container=self, parent_element=self, object_id='#txt_title')
        #lab_title.font = owner.titl_font
        lab_subtitle = UILabel(Rect((10, 35), (self.rect.width-10, 20)), text=subtitle, manager=manager, container=self, parent_element=self, object_id='#txt_subtitle')
        #lab_subtitle.font = owner.subtitl_font
        lab_author = UILabel(Rect((10, 55), (self.rect.width-10, 20)), text=author, manager=manager, container=self, parent_element=self, object_id='#txt_author')
        #lab_author.font = owner.creature_font

class EnviroWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        super().__init__(rect, manager=manager, window_display_title='Enviroment Info', object_id="#enviro_win", visible=True)
        self.manager = manager
        i=0
        self.labs = {}
        for key, val in data.items():
            lab1 = UILabel(Rect((10, 15*i+5), (90, 15)), text=f"{key}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_key'+str(i))
            lab2 = UILabel(Rect((120, 15*i+5), (self.rect.width/2-20, 15)), text=f"{val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_val'+str(i))
            i+=1
            self.labs[key] = (lab1, lab2)
        self.btn_close = UIButton(Rect((rect.width/2-btn_w/2, (15+15*i)), (btn_w, btn_h)), text='Close', manager=self.manager, container=self, parent_element=self, object_id='#btn_quit')
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        if self.refresh <= 0:
            self.refresh = 1
            data = data
            for key, val in data.items():
                self.labs[key][0].set_text(f"{key}:")
                self.labs[key][1].set_text(f"{val}")

class CreatureWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        super().__init__(rect, manager=manager, window_display_title='Creature Info', object_id="#creature_win", visible=True)
        self.manager = manager
        i=0
        self.labs = {}
        for key, val in data.items():
            if key != 'states':
                lab1 = UILabel(Rect((5, 15*i+5), (70, 15)), text=f"{key}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_key'+str(i))
                lab2 = UILabel(Rect((85, 15*i+5), (self.rect.width/2-15, 15)), text=f"{val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_val'+str(i))
            else:
                lab1 = UILabel(Rect((5, 15*i+5), (10, 15)), text=f"{key}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_key'+str(i))
                lab2 = UILabel(Rect((16, 15*i+5), (self.rect.width-21, 15)), text=f"{val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info_val'+str(i))
            i+=1
            self.labs[key] = (lab1, lab2)
        btn_w = 80; btn_h = 20
        self.btn_ancestors = UIButton(Rect((rect.width/2-btn_w/2, (15+15*i)), (btn_w, btn_h)), text='ANCESTORS', manager=self.manager, container=self, parent_element=self, object_id="#btn_ancestors")
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        if self.refresh <= 0:
            self.refresh = 1
            data = data
            for key, val in data.items():
                self.labs[key][0].set_text(f"{key}:")
                self.labs[key][1].set_text(f"{val}")

class AncestorsWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, history: list):
        super().__init__(rect, manager=manager, window_display_title='Ancestors', object_id="#genealogy_win", visible=True)
        self.manager = manager
        i=0
        self.labels = []
        for (specie, gen, time) in history:
            lab = UILabel(Rect((5, 10*i+2), (190, 15)), text=f"T({time}) \t {specie} \t GEN({gen})", manager=self.manager, container=self, parent_element=self, object_id='lab_ancestor'+str(i))
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
        btn_list = [('Creature Info', '#creature_win'), ('Enviroment Info', '#enviro'), ('Ranking', '#rank'), ('Credits', '#credits'), ('Back', '#info_back')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s+btn_h)*i), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
            buttons.append(btn)
            i += 1

class SaveMenuWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Save Menu', object_id="#save_menu", visible=True)
        self.manager = manager
        btn_list = [('Save Progress', '#save_progress'), ('Save Creature', '#save_creature'), ('Duplicate Sim', '#duplicate_sim'), ('Back', '#save_back')]
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
        #self.ui_mgr = UIManager(window_resolution=(self.view[0], self.view[1]), theme_path='blue.json')
        self.ui_mgr = UIManager(window_resolution=view, theme_path='res/themes/blue.json')
        #self.ui_mgr.load_theme('blue.json')
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
        self.rank_win = None
        self.credits_win = None
        self.history_win = None
        self.ancestors_win = None
        self.rebuild_ui(self.view)

    def rebuild_ui(self, new_size: tuple):         
        self.ui_mgr.set_window_resolution(new_size)
        self.ui_mgr.clear_and_reset()
        self.size = new_size
        self.create_title(new_size)
        #self.create_enviro_win()
        btn_pos = Rect((round(cfg.SCREEN[0]-50), 10), (40, 40))
        self.create_menu_btn(btn_pos)
        #self.create_title(new_size)

    def create_menu_btn(self, rect: Rect):
        self.btn_menu = UIButton(rect, 'MENU', self.ui_mgr, object_id='#btn_menu')

    def create_custom_btn(self, rect: Rect, title: str, obj_id: str):
        btn = UIButton(relative_rect=rect, text=title, manager=self.ui_mgr, object_id=obj_id)
        return btn

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
        h = 250
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.info_menu = InfoMenuWindow(manager=self.ui_mgr, rect=pos)

    def save_creature(self, selected: Life):
        if not isinstance(selected, Creature):
            return
        else:
            pass

    def create_save_menu(self):
        w = 250
        h = 250
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.save_menu = SaveMenuWindow(manager=self.ui_mgr, rect=pos)

    def create_new_sim(self):
        w = 300
        h = 150
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h+25))
        self.main_menu.kill()
        self.new_sim = NewSimWindow(manager=self.ui_mgr, rect=pos)

    def create_load_menu(self):
        w = 300
        h = 400
        pos = Rect((self.cx-w/2, self.cy-h+100), (w, h+200))
        self.load_menu = LoadWindow(manager=self.ui_mgr, rect=pos)

    def create_info_win(self, text: str, title: str):
        w = 400
        h = 150
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.info_win = InfoWindow(manager=self.ui_mgr, rect=pos, text=text, title=title)

    def create_credits_win(self, title: str, subtitle: str, author: str, bar_text: str):
        w = 250
        h = 140
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.credits_win = CreditsWindow(owner=self.owner, manager=self.ui_mgr, rect=pos, title=title, subtitle=subtitle, author=author, bar_text=bar_text)

    def create_rank_win(self):
        w = 290
        h = 350
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.rank_win = RankWindow(self, manager=self.ui_mgr, rect=pos)

    def update_ranking(self, ranking1: list, ranking2: list) -> dict:
        return [ranking1, ranking2]

    def create_title(self, scr_size: tuple):
        w = 350
        h = 25
        h2 = 20
        title_rect = Rect((round(cfg.SCREEN[0]/2-w/2), (10)), (w, h))
        #subtitle_rect = Rect((round(cfg.SCREEN[0]/2-w/2), (40)), (w, h2))
        world_rect = Rect((round(cfg.SCREEN[0]/2-w/2), (35)), (w, h2))
        self.title = UILabel(relative_rect=title_rect, text=TITLE, manager=self.ui_mgr, object_id='#lab_title')
        #self.subtitle = UILabel(relative_rect=subtitle_rect, text=SUBTITLE, manager=self.ui_mgr, object_id='#lab_subtitle')
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
        data['NEURO_TIME'] = ''
        data['PHYSIC_TIME'] = ''
        self.enviro_win = EnviroWindow(manager=self.ui_mgr, rect=Rect((0, 0), (200, 125)), data=data, dT=dT)

    def create_creature_win(self, dT: float):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.update_creature_win()
            self.creature_win = CreatureWindow(manager=self.ui_mgr, rect=Rect((200, 0), (220, 300)), data=data, dT=dT)

    def create_ancestors_win(self, dT: float):
        if self.ancestors_win:
            self.ancestors_win.kill()
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            count = len(data)
            height = 2 + 15 * count
            self.ancestors_win = AncestorsWindow(manager=self.ui_mgr, rect=Rect((500, 0), (200, height)), history=data)

    def create_history_win(self, dT: float):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            self.history_win = CreatureHistoryWindow(manager=self.ui_mgr, rect=Rect((200, 200), (150, 400)), parents=data, dT=dT)

    def update_creature_history(self, dT):
        if self.owner.enviro.selected and isinstance(self.owner.enviro.selected, Creature):
            data = self.owner.enviro.selected.genealogy
            self.history_win.Update(data, dT)

    def update_creature_win(self) -> dict:
        if not self.owner.enviro.selected or not isinstance(self.owner.enviro.selected, Creature):
            data = {}
            data['SPECIE'] = ''
            data['GENERATION'] = ''
            data['FOOD'] = ''
            data['ENERGY'] = ''
            data['ENERGY'] = ''
            data['POWER'] = ''
            data['SPEED'] = ''
            data['SIZE'] = ''
            data['MUTATIONS'] = ''
            data['CHILDS'] = ''
            data['FITNESS'] = ''
            data["LIFETIME"] = ''
            data["REP_TIME"] = ''
            data['S'] = ''
            return data
        data = {}
        data['SPECIE'] = self.owner.enviro.selected.name
        data['GENERATION'] = str(self.owner.enviro.selected.generation)
        data['FOOD'] = str(self.owner.enviro.selected.food)
        data['ENERGY'] = str(round(self.owner.enviro.selected.energy))+'/'+str(round(self.owner.enviro.selected.max_energy))
        data['WATER'] = str(round(self.owner.enviro.selected.water))+'/'+str(round(self.owner.enviro.selected.max_energy))
        data['POWER'] = str(self.owner.enviro.selected.power)
        data['SPEED'] = str(self.owner.enviro.selected.speed)
        data['SIZE'] = str(self.owner.enviro.selected.size)
        data['MUTATIONS'] = str(self.owner.enviro.selected.mutations)
        data['CHILDS'] = str(self.owner.enviro.selected.childs)
        data['BORN|KILL'] = str(self.owner.enviro.selected.childs)+'|'+str(self.owner.enviro.selected.kills)
        data['FITNESS'] = str(round(self.owner.enviro.selected.fitness))
        data["LIFETIME"] = str(round(self.owner.enviro.selected.life_time))
        data["REP_TIME"] = str(round(self.owner.enviro.selected.reproduction_time))
        states = []
        if self.owner.enviro.selected.hide:
            states.append(' [H]')
        if self.owner.enviro.selected._attack:
            states.append(' [A]')
        if self.owner.enviro.selected.run:
            states.append(' [R]')
        if self.owner.enviro.selected.on_water:
            states.append(' [W]')
        if self.owner.enviro.selected._eat:
            states.append(' [E]')
            if self.owner.enviro.selected.on_water[0]:
                states.append(' [D]')
        data['S'] = ''
        for state in states:
            data['S'] += state
        return data

    def select_map(self):
        w = 300
        h = 100
        scr_w = self.owner.w
        scr_h = self.owner.h
        pos = Rect((scr_w/2-w/2, scr_h/2-h/2), (w, h))
        self.main_menu.kill()
        self.map_sim = MapWindow(manager=self.ui_mgr, rect=pos)

    def update_enviroment(self, dT: float) -> dict:
        data = {}
        data['dT'] = str(round(dT, 3)) + 's'
        data['TIME'] = str(self.owner.enviro.cycles*6000 + round(self.owner.enviro.time)) + 's'
        data['CREATURES'] = 'H:'+str(self.owner.enviro.herbivores)+'|C:'+str(self.owner.enviro.carnivores)
        data['PLANTS'] = str(len(self.owner.enviro.plant_list))
        data['NEURO_TIME'] = str(round(self.owner.enviro.neuro_avg_time*1000, 1)) + 'ms'
        data['PHYSIC_TIME'] = str(round(self.owner.enviro.physics_avg_time*1000, 1)) + 'ms'
        return data

    def process_event(self, event, dt: float):
        self.ui_mgr.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == '#btn_menu':
                    self.create_main_menu()
                elif event.ui_object_id == '#menu_win.#btn_resume':
                    self.main_menu.kill()
                elif event.ui_object_id == '#menu_win.#btn_sim':
                    self.main_menu.kill()
                    self.create_new_sim()
                elif event.ui_object_id == '#menu_win.#btn_map':
                    self.main_menu.kill()
                    self.select_map()
                elif event.ui_object_id == '#menu_win.#save_menu':
                    self.main_menu.kill()
                    self.create_save_menu()
                elif event.ui_object_id == '#save_menu.#save_progress':
                    self.owner.save_project()
                    self.save_menu.kill()
                elif event.ui_object_id == '#save_menu.#save_creature':
                    self.save_menu.kill()
                    self.save_creature(selected=self.owner.enviro.selected)
                elif event.ui_object_id == '#save_menu.#save_back':
                    self.save_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#menu_win.#btn_info':
                    self.main_menu.kill()
                    self.create_info_menu()
                    #self.create_credits_win(title=TITLE, subtitle=SUBTITLE, author=AUTHOR, bar_text=TITLE)
                elif event.ui_object_id == '#credits_win.#btn_close':
                    self.credits_win.kill()
                elif event.ui_object_id == '#menu_win.#btn_load':
                    self.main_menu.kill()
                    self.create_load_menu()
                elif event.ui_object_id == '#new_win.#btn_cancel':
                    self.new_sim.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#new_win.#btn_accept':
                    new_name = self.new_sim.edit.get_text()                    
                    self.owner.enviro.project_name = new_name
                    self.new_project_name(new_name)
                    self.new_sim.kill()
                    self.create_title(cfg.SCREEN)
                    self.owner.enviro.create_enviro()
                    self.create_info_win(text='Project created with name: ' + new_name, title=new_name)
                elif event.ui_object_id == '#menu_win.#btn_set':
                    self.main_menu.kill()
                    self.create_settings()
                elif event.ui_object_id == '#load_win.#btn_del_':
                    sim_to_del = event.ui_element.destroy_id
                    if sim_to_del == self.owner.project_name:
                        pass
                    else:
                        pass
                elif event.ui_object_id[0: 15] == '#load_win.#btn_':
                    project_name = event.ui_element.text
                    self.owner.enviro.project_name = project_name
                    self.owner.load_last(project_name)
                    self.load_menu.kill()   
                    self.kill_title()
                    self.create_title(cfg.SCREEN) 
                    self.create_info_win(text=f"Project {project_name.upper()} has been loaded", title='Load Simulation')
                elif event.ui_object_id == '#load_win.#load_back':
                    self.load_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#info_win.#btn_info':
                    self.info_win.kill()
                elif event.ui_object_id == '#set_win.#btn_back':
                    self.set_win.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#set_win.#btn_rel_set':
                    self.reload_config()
                elif event.ui_object_id == '#info_menu.#enviro':
                    self.info_menu.kill()
                    self.create_enviro_win(dt)
                elif event.ui_object_id == '#info_menu.#creature_win':
                    self.info_menu.kill()
                    self.create_creature_win(dt)
                elif event.ui_object_id == '#creature_win.#btn_ancestors':
                    self.create_ancestors_win(dt)
                elif event.ui_object_id == '#info_menu.#rank':
                    self.info_menu.kill()
                    self.create_rank_win()
                elif event.ui_object_id == '#info_menu.#credits':
                    self.info_menu.kill()
                    self.create_credits_win(title=TITLE, subtitle=SUBTITLE, author=AUTHOR, bar_text=TITLE)
                elif event.ui_object_id == '#info_menu.#info_back':
                    self.info_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#rank_win.#btn_quit':
                    self.rank_win.kill()
                elif event.ui_object_id == '#enviro_win.#btn_quit':
                    self.enviro_win.kill()
                elif event.ui_object_id == '#menu_win.#btn_quit':
                    pygame.quit()
                    sys.exit(0)
            return True
        else:
            return False

    def reload_config(self):
        self.set_win.kill()
        cfg.load_from_file('config.json')

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
        if self.history_win and self.owner.enviro.selected:
            self.update_creature_history(dT=dT)

    def draw_ui(self, screen):
        self.ui_mgr.draw_ui(screen)

    def new_project_name(self, name: str):
        try:
            os.mkdir('saves/' + name)
        except FileExistsError:
            pass
        f = open("saves/projects.json", "r+")
        proj_list = f.read()
        f.close()
        projects_list = json.loads(proj_list)
        if not name in projects_list["projects"]:
            projects_list["projects"].append(name)
            proj_json = json.dumps(projects_list)
            f = open("saves/projects.json", "w+")
            f.write(proj_json)
            f.close()
            return True
        else:
            return False

class NeuroGUI():

    def __init__(self, owner: object, view: tuple):
        self.view = view
        self.owner = owner
        self.ui_mgr = UIManager(window_resolution=(self.view[0], self.view[1]), theme_path='res/themes/blue.json')
        #self.ui_mgr.preload_fonts([
        #    {'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
        #    {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
        #    {'name': 'fira_code', 'point_size': 9, 'style': 'regular'},
        #    {'name': 'fira_code', 'point_size': 12, 'style': 'regular'},
        #    {'name': 'fira_code', 'point_size': 14, 'style': 'regular'},
        #    {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
        #])
        self.btn_names = [('Select Neural Network', '#btn_select_net')]
        self.rebuild_viewer((self.view[0], self.view[1]))
        self.buttons = []

    def create_custom_btn(self, rect: Rect, title: str, obj_id: str):
        btn = UIButton(relative_rect=rect, text=title, manager=self.ui_mgr, object_id=obj_id)
        return btn

    def rebuild_viewer(self, size: tuple):
        self.ui_mgr.set_window_resolution(size)
        self.ui_mgr.clear_and_reset()
        self.size = size
        for n, i in self.btn_names:
            btn_pos =  Rect(40, 40, 40, 40)
            btn = self.create_custom_btn(rect=btn_pos, title=n, obj_id=i)
            self.buttons.append(btn)

    def process_event(self, event):
        self.ui_mgr.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == '#btn_select_net':
                    self.create_select_net()
                elif event.ui_object_id == '#win_sel_net.#btn_cancel':
                    self.select_net.kill()
                elif event.ui_object_id == '#win_sel_net.#btn_accept':
                    new_name = self.select_net.edit.get_text()                    
                    self.select_net.kill()
                    self.owner.select_net(new_name)

    def create_select_net(self):
        w = 300
        h = 100
        scr_w = self.owner.w
        scr_h = self.owner.h
        pos = Rect((scr_w/2-w/2, scr_h/2-h/2), (w, h))
        self.select_net = SelectNet(manager=self.ui_mgr, rect=pos)
