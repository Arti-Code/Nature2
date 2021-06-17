import os
import sys
import json
from collections import deque
import pygame
import pygame_gui
from copy import copy
from pygame import Rect
from pygame_gui import UIManager, PackageResource
from pygame_gui.elements import UITextBox, UIWindow, UIButton, UILabel, UITextEntryLine, UIPanel
from lib.config import *


TITLE = "NATURE v0.2.1"
SUBTITLE = "2019-2021 Artur Gwoździowski  v0.2.1"
btn_w = 150
btn_h = 30
btn_s = 10

class NewSimWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):

        super().__init__(rect, manager=manager, window_display_title='New Simulation', object_id="#new_win", visible=True)
        self.manager = manager
        self.label = UILabel(Rect((25, 10), (250, 10)), text='Enter New Project Name', manager=manager, container=self, parent_element=self)
        self.edit = UITextEntryLine(Rect((75, 30), (150, 20)), manager=manager, container=self, parent_element=self)
        self.cancel = UIButton(Rect((50, 70), (75, 30)), text='Cancel', manager=manager, container=self, parent_element=self, object_id='#btn_cancel')
        self.accept = UIButton(Rect((175, 70), (75, 30)), text='Accept', manager=manager, container=self, parent_element=self, object_id='#btn_accept')

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
        btn_list = [('New Simulation', '#btn_sim'), ('Select Terrain', '#btn_map'), ('Save Simulation', '#btn_save'), ('Load Simulation', '#btn_load'), ('Settings', '#btn_set'), ('Quit', '#btn_quit')]
        buttons = []
        i = 1
        for (txt, ident) in btn_list:
            btn = UIButton(Rect((50, (btn_s+btn_h)*i), (btn_w, btn_h)), text=txt, manager=self.manager, container=self, parent_element=self, object_id=ident)
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

class InfoWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, text: str, title: str=''):
        super().__init__(rect, manager=manager, window_display_title=title, object_id="#info_win", visible=True)
        self.manager = manager
        btn = UIButton(Rect((round((self.rect.width/2)-(btn_w/2)), 60), (btn_w, btn_h)), text='Accept', manager=self.manager, container=self, parent_element=self, object_id='#btn_info')
        msg = UILabel(Rect((10, 15), (self.rect.width-10, 40)), text=text, manager=manager, container=self, parent_element=self, object_id='txt_msg')

class EnviroWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect, data: dict, dT: float):
        super().__init__(rect, manager=manager, window_display_title='Enviroment Info', object_id="#enviro_win", visible=True)
        self.manager = manager
        i=0
        self.labs = {}
        for key, val in data.items():
            lab = UILabel(Rect((10, 10*i+5), (self.rect.width-10, 40)), text=f"{key}: {val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info'+str(i))
            i+=1
            self.labs[key] = lab
        self.btn_close = UIButton(Rect((75, (25+10*i+5)), (50, 20)), text='Close', manager=self.manager, container=self, parent_element=self, object_id='#btn_quit')
        self.refresh = 0
        self.Update(data, dT)

    def Update(self, data: dict, dT: float):
        self.refresh -= dT
        if self.refresh <= 0:
            self.refresh = 1
            #self.labs.clear()
            for key, val in data.items():
                #self.labs[key] = UILabel(Rect((10, 15*i), (self.rect.width-10, 40)), text=f"{key}: {val}", manager=self.manager, container=self, parent_element=self, object_id='lab_info'+str(i))
                self.labs[key].set_text(f"{key}: {val}")

class SettingsWindow(UIWindow):

    def __init__(self, manager: UIManager, rect: Rect):
        super().__init__(rect, manager=manager, window_display_title='Settings', object_id="#set_win", visible=True)
        self.manager = manager
        btn_list = [('Enviroment Info', '#btn_gui'), ('Set Enviroment', '#btn_enviro'), ('Back', '#btn_back')]
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
        self.cx = round(self.view[0]/2)
        self.cy = round(self.view[1]/2)
        #self.ui_mgr = UIManager(window_resolution=(self.view[0], self.view[1]), theme_path='blue.json')
        self.ui_mgr = UIManager(window_resolution=view, theme_path='res/themes/blue.json')
        self.ui_mgr.preload_fonts(font_list=[
                    {'name': 'fira_code10b', 'point_size': 10, 'style': 'bold'},
                    {'name': 'fira_code10r', 'point_size': 10, 'style': 'regular'},
                    {'name': 'fira_code9r', 'point_size': 9, 'style': 'regular'},
                    {'name': 'fira_code', 'point_size': 12, 'style': 'regular'},
                    {'name': 'fira_code', 'point_size': 14, 'style': 'regular'},
                    {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
        ])
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
        self.enviro_win = None
        self.rebuild_ui(self.view)

    def rebuild_ui(self, new_size: tuple):         
        self.ui_mgr.set_window_resolution(new_size)
        self.ui_mgr.clear_and_reset()
        self.size = new_size
        self.create_title(new_size)
        #self.create_enviro_win()
        btn_pos = Rect((round(new_size[0]-50), 10), (40, 40))
        self.create_menu_btn(btn_pos)
        #self.create_title(new_size)

    def create_menu_btn(self, rect: Rect):
        self.btn_menu = UIButton(rect, 'MENU', self.ui_mgr, object_id='#btn_menu')

    def create_custom_btn(self, rect: Rect, title: str, obj_id: str):
        btn = UIButton(relative_rect=rect, text=title, manager=self.ui_mgr, object_id=obj_id)
        return btn

    def create_main_menu(self):
        w = 250
        h = 300
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.main_menu = MenuWindow(manager=self.ui_mgr, rect=pos)

    def create_settings(self):
        w = 250
        h = 300
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
        self.set_win = SettingsWindow(manager=self.ui_mgr, rect=pos)

    def create_new_sim(self):
        w = 300
        h = 140
        pos = Rect((self.cx-w/2, self.cy-h/2), (w, h))
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

    def create_title(self, scr_size: tuple):
        w = 350
        h = 40
        h2 = 15
        title_rect = Rect((round(scr_size[0]/2-w/2), (10)), (w, h))
        subtitle_rect = Rect((round(scr_size[0]/2-w/2), (35)), (w, h2))
        world_rect = Rect((round(scr_size[0]/2-w/2), (50)), (w, h))
        self.title = UILabel(relative_rect=title_rect, text=TITLE, manager=self.ui_mgr, object_id='#lab_title')
        self.subtitle = UILabel(relative_rect=subtitle_rect, text=SUBTITLE, manager=self.ui_mgr, object_id='#lab_subtitle')
        #self.world = UILabel(relative_rect=world_rect, text=self.owner.project_name, manager=self.ui_mgr, object_id='#lab_world')

    def kill_title(self):
        self.title.kill()
        self.subtitle.kill()
        self.world.kill()

    def create_enviro_win(self, dT: float):
        data = {}
        data['FPS'] = str(round(self.owner.enviro.fps))
        data['TIME'] = str(self.owner.enviro.Time())
        data['CREATURES'] = str(len(self.owner.enviro.my_creatures))
        data['PREDATORS'] = str(self.owner.enviro.hunter_num)
        data['HERBIVORES'] = str(self.owner.enviro.herbs_num)
        data['PLANTS'] = str(len(self.owner.enviro.my_plants))
        if self.owner.enviro.dt:
            data['DELTA'] = str(round(self.owner.enviro.dt*1000))
        self.enviro_win = EnviroWindow(manager=self.ui_mgr, rect=Rect((5, 5), (200, 150)), data=data, dT=dT)

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
        data['FPS'] = str(round(self.owner.enviro.fps))
        data['TIME'] = str(self.owner.enviro.Time())
        data['CREATURES'] = str(len(self.owner.enviro.my_creatures))
        data['PREDATORS'] = str(self.owner.enviro.hunter_num)
        data['HERBIVORES'] = str(self.owner.enviro.herbs_num)
        data['PLANTS'] = str(len(self.owner.enviro.my_plants))
        if dT:
            data['DELTA'] = str(round(dT, 3))
        return data

    def process_event(self, event):
        self.ui_mgr.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == '#btn_menu':
                    self.create_main_menu()
                elif event.ui_object_id == '#menu_win.#btn_sim':
                    self.main_menu.kill()
                    self.create_new_sim()
                elif event.ui_object_id == '#menu_win.#btn_map':
                    self.main_menu.kill()
                    self.select_map()
                elif event.ui_object_id == '#menu_win.#btn_save':
                    project_name = self.owner.project_name
                    self.owner.SaveProject(project_name)
                    self.main_menu.kill()
                    self.create_info_win(text=f"Project {project_name.upper()} has been saved", title='Save Simulation')
                elif event.ui_object_id == '#menu_win.#btn_load':
                    self.main_menu.kill()
                    self.create_load_menu()
                elif event.ui_object_id == '#new_win.#btn_cancel':
                    self.new_sim.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#new_win.#btn_accept':
                    new_name = self.new_sim.edit.get_text()                    
                    self.owner.project_name = new_name
                    self.new_project_name(new_name)
                    self.new_sim.kill()
                    self.owner.enviro.CreateWorld(dT)
                    self.create_info_win(text='Project created with name: ' + new_name, title=new_name)
                elif event.ui_object_id == '#menu_win.#btn_set':
                    self.main_menu.kill()
                    self.create_settings()
                elif event.ui_object_id == '#load_win.#btn_del_':
                    sim_to_del = event.ui_element.destroy_id
                    if sim_to_del == self.owner.project_name:
                        pass
                        #print(f"{sim_to_del} already in use!")
                    else:
                        pass
                        #print(f"{sim_to_del} deleted!")
                elif event.ui_object_id[0: 15] == '#load_win.#btn_':
                    project_name = event.ui_element.text
                    self.owner.project_name = project_name
                    self.owner.LoadLast(project_name)
                    self.load_menu.kill()   
                    self.kill_title()
                    self.create_title((self.view[0], self.view[1])) 
                    self.create_info_win(text=f"Project {project_name.upper()} has been loaded", title='Load Simulation')
                elif event.ui_object_id == '#load_win.#load_back':
                    self.load_menu.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#info_win.#btn_info':
                    self.info_win.kill()
                elif event.ui_object_id == '#set_win.#btn_back':
                    self.set_win.kill()
                    self.create_main_menu()
                elif event.ui_object_id == '#set_win.#btn_gui':
                    self.set_win.kill()
                    self.create_enviro_win(dT)
                elif event.ui_object_id == '#enviro_win.#btn_quit':
                    self.enviro_win.kill()
                elif event.ui_object_id == '#menu_win.#btn_quit':
                    pygame.quit()
                    sys.exit(0)

    def update(self, dt: float):
        self.ui_mgr.update(dt)
        if self.enviro_win:
            data = self.update_enviroment(dt)
            self.enviro_win.Update(data, dt)

    def draw_ui(self, screen):
        self.ui_mgr.draw_ui(screen)

    def new_project_name(self, name: str):
        PROJECT_NAME = copy(name)
        try:
            os.mkdir('saves/' + name)
            #print(f"new project name set: {name.upper()} with new directory")
        except FileExistsError:
            pass
            #print(f"project name set: {name.upper()} but it was already existing")
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
