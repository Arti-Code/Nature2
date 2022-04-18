from copy import copy, deepcopy
from random import random, randint
from math import log, sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
from statistics import mean
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pygame.font import Font
from pygame.math import Vector2
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.life import Life
from lib.math2 import flipy, clamp
from lib.sensor import Sensor
from lib.net import Network
from lib.species import random_name, modify_name
from lib.config import cfg
from lib.utils import log_to_file
from lib.camera import Camera
from lib.vision import Vision

class Creature(Life):

    def __init__(self, screen: Surface, space: Space, time: int, collision_tag: int, position: Vec2d, genome: dict=None, color0: Color=Color('grey'), color1: Color=Color('skyblue'), color2: Color=Color('orange'), color3: Color=Color('red')):
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
        self.angle = random()*2*PI
        self.output = [0, 0, 0, 0, 0]
        self.generation = 0
        self.fitness = 0
        self.neuro = Network()
        self.normal: Vec2d=Vec2d(0, 0)
        self.signature: list=[]
        self.childs = 0
        self.kills = 0
        self.genealogy = []
        self.mutations_num = [(0, 0), (0, 0)]
        if genome == None:
            self.random_build(color0, color1, color2, color3, time)
            self.signature = self.get_signature()
        else:
            self.mutations_num = self.genome_build(genome)
            if not self.compare_signature(self.get_signature(), genome['signature'], cfg.DIFF):
                self.signature = self.get_signature()
                self.name = modify_name(genome['name'])
                self.add_specie(self.name, self.generation, time)
        self.shape = Circle(self, self.size)
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        self.eye_colors = {}
        self.visual_range = cfg.SENSOR_RANGE
        self.sensors = []
        self.side_angle = 0
        self.sensor_angle = (1 - random())*cfg.SENSOR_MAX_ANGLE
        self.sensor_angle = ((random()+1)/2)*cfg.SENSOR_MAX_ANGLE
        self.vision = Vision(self, cfg.SENSOR_RANGE, cfg.SENSOR_MAX_ANGLE, (0.0, 0.0), "vision")
        space.add(self.vision)
        self.mem_time = 0
        self.max_energy = self.size*cfg.SIZE2ENG
        self.reproduction_time = cfg.REP_TIME
        self.energy = self.max_energy
        for sensor in self.sensors:
           space.add(sensor.shape)
        self.moving: float=0.0
        self.eating: bool=False
        self.attacking: bool=False
        self.turning: float=0.0
        self.pain: bool=False
        self.running: bool=False
        self.life_time: float=0.0
        self.run_time = cfg.RUN_TIME
        self.hidding: bool=False
        self.hide_ref_time = 0.0
        self.run_ref_time = 0.0
        self.on_water = False
        self.neuro.CalcNodeMutMod()

    def genome_build(self, genome: dict) -> list[tuple]:
        self.color0 = Color(genome['color0'][0], genome['color0'][1], genome['color0'][2], genome['color0'][3])
        self.color1 = Color(genome['color1'][0], genome['color1'][1], genome['color1'][2], genome['color1'][3])
        self.color2 = Color(genome['color2'][0], genome['color2'][1], genome['color2'][2], genome['color2'][3])
        self.color3 = Color(genome['color3'][0], genome['color3'][1], genome['color3'][2], genome['color3'][3])
        self._color0 = self.color0
        self._color1 = self.color1
        self._color2 = self.color2
        self._color3 = self.color3
        self.neuro = genome['neuro']
        self.size = genome['size'] + randint(-1, 1)
        self.mutations = genome['mutations'] + randint(-1, 1)
        self.power = genome['power'] + randint(-1, 1)
        self.food = genome['food'] + randint(-1, 1)
        self.speed = genome['speed'] + randint(-1, 1)
        self.size = clamp(self.size, cfg.CREATURE_MIN_SIZE, cfg.CREATURE_MAX_SIZE)
        self.mutations = clamp(self.mutations, 1, 10)
        self.power = clamp(self.power, 1, 10)
        self.food = clamp(self.food, 1, 10)
        self.speed = clamp(self.speed, 1, 10)
        self.generation = genome['gen']+1
        self.genealogy = genome['genealogy']
        self.name = genome['name']
        mutations = self.neuro.Mutate(mutations_rate=self.mutations)
        self.signature = genome['signature']
        return mutations

    def random_build(self, color0: Color, color1: Color, color2: Color, color3: Color, time: int):
        #self.color0 = color0
        self.color0 = Color('black')
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        #self._color0 = color0
        self._color0 = Color('black')
        self._color1 = color1
        self._color2 = color2
        self._color3 = color3
        self.food = randint(1, 10)
        #self.meat = randint(1, 10)
        self.mutations = randint(1, 10)
        self.power = randint(1, 10)
        self.speed = randint(1, 10)
        self.size = randint(cfg.CREATURE_MIN_SIZE, cfg.CREATURE_MAX_SIZE)
        self.neuro.BuildRandom(cfg.NET, cfg.LINKS_RATE)
        self.name = random_name(3, True)
        self.add_specie(self.name, self.generation, time)

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        x = self.position.x; y = flipy(self.position.y)
        r = self.shape.radius
        rect = Rect(x-r, y-r, 2*r, 2*r)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        self.rel_pos = rel_pos
        rx = rel_pos.x
        ry = rel_pos.y
        super().draw(screen, camera, selected)
        rot = self.rotation_vector
        color0 = self.color0
        color1 = self.color1
        color2 = self.color2
        a = 255
        if self.hidding:
            color0.a = 40
            color1.a = 40
            color2.a = 40
            a = 40
        else:
            color0.a = 255
            color1.a = 255
            color2.a = 255
            a = 255
        marked = False
        if selected == self:
            marked = True
        gfxdraw.aacircle(screen, int(rx), int(ry), int(r), color2)
        gfxdraw.filled_circle(screen, int(rx), int(ry), int(r), color2)
        gfxdraw.aacircle(screen, int(rx), int(ry), int(r-1), self.color2)
        gfxdraw.filled_circle(screen, int(rx), int(ry), int(r-1), color2)
        if self.running:
            shadow = color2
            shadow.a = 80
            for i in range(3):
                sx = rx-(rot.x*r*(0.8*(i+1)))
                sy = ry-(rot.y*r*(0.8*(i+1)))
                gfxdraw.aacircle(screen, int(sx), int(sy), int(r), shadow)
                gfxdraw.filled_circle(screen, int(sx), int(sy), int(r), shadow)
                gfxdraw.aacircle(screen, int(sx), int(sy), int(r-1), shadow)
                gfxdraw.filled_circle(screen, int(sx), int(sy), int(r-1), shadow)
        if r > 2:
            x2 = round(rx + rot.x*(r/1.6))
            y2 = round(ry + rot.y*(r/1.6))
            x3 = round(rx + rot.x*(r/1.1))
            y3 = round(ry + rot.y*(r/1.1))
            r2 = round(r/2)
            r: int; g: int; b: int
            if self.food >= 6:
                r = round(25.5*self.food)
                g = round(255-25.5*self.food)
                b = 0
                r +=50
                g -=50
                r = clamp(r, 0, 255)
                g = clamp(g, 0, 255)
            else:
                r = round(25.5*(self.food-1))
                g = round(255-25.5*(self.food+1))
                b = 0
                r -=50
                g +=50
                r = clamp(r, 0, 255)
                g = clamp(g, 0, 255)
            gfxdraw.aacircle(screen, int(x2), int(y2), int(r2), Color(175, 175, 175, a))    
            gfxdraw.filled_circle(screen, int(x2), int(y2), int(r2), Color(175, 175, 175, a))
            gfxdraw.aacircle(screen, int(rx), int(ry), int(r2), Color(r, g, b, a))
            gfxdraw.filled_circle(screen, int(rx), int(ry), int(r2), Color(r, g, b, a))
            gfxdraw.filled_circle(screen, int(x3), int(y3), int(r2*0.67), Color('black'))
        self.vision.draw(screen=screen, camera=camera, rel_position=rel_pos, selected=marked)
        self.color0 = self._color0
        self.draw_energy_bar(screen, rx, ry)
        #self.reset_collisions()
        #self.vision.reset_range()
        #self.draw_water_bar(screen, rx, ry)
        #self.draw_name(screen)
        #self.draw_normal(screen)
        return True

    def draw_normal(self, screen):
        if self.normal != None:
            gfxdraw.line(screen, int(self.position.x), int(flipy(self.position.y)), int(self.position.x+self.normal.x*50), int(flipy(self.position.y+self.normal.y*50)), Color('yellow'))
            #self.normal = None

    def draw_detectors(self, screen, rel_pos: Vector2):
        for detector in self.sensors:
            detector.draw(screen=screen, rel_pos=rel_pos)
        self.collide_creature = False
        self.collide_plant = False
        self.collide_water = False
        self.collide_meat = False

    def reset_collisions(self):
        self.collide_creature = False
        self.collide_plant = False
        self.collide_water = False
        self.collide_meat = False
        
    def draw_name(self, camera: Camera):
        rpos = camera.rel_pos(Vector2((self.position.x-20), flipy(self.position.y+14)))
        return self.name, rpos.x, rpos.y

    def draw_dist(self, camera: Camera):
        rpos = camera.rel_pos(Vector2((self.position.x-50), flipy(self.position.y+30)))
        enemy_dir = '-'; plant_dir = '-'; meat_dir = '-';
        enemy_ang = round(self.vision.enemy['ang'], 1)
        plant_ang = round(self.vision.plant['ang'], 1)
        meat_ang = round(self.vision.meat['ang'], 1)
        """ if enemy_ang >= 0.1:
            if enemy_ang > 0.5:
                enemy_dir = '>>'
            else:
                enemy_dir = '>'
        elif enemy_ang <= -0.1:
            if enemy_ang < -0.5:
                enemy_dir = '<<'
            else:
                enemy_dir = '<'
        if plant_ang >= 0.1:
            if plant_ang > 0.5:
                plant_dir = '>>'
            else:
                plant_dir = '>'
        elif plant_ang <= -0.1:
            if plant_ang < -0.5:
                plant_dir = '<<'
            else:
                plant_dir = '<'
        if meat_ang >= 0.1:
            if meat_ang > 0.5:
                meat_dir = '>>'
            else:
                meat_dir = '>'
        elif meat_ang <= -0.1:
            if meat_ang < -0.5:
                meat_dir = '<<'
            else:
                meat_dir = '<' """
        #txt = "{:^}[{:^}] | {:^}[{:^}] | {:^}[{:^}]".format(round(sqrt(self.vision.max_dist_enemy)), enemy_dir, round(sqrt(self.vision.max_dist_plant)), plant_dir, round(sqrt(self.vision.max_dist_meat)), meat_dir)
        #return f"{(round(sqrt(self.vision.max_dist_enemy)))}[{enemy_dir}] | {(round(sqrt(self.vision.max_dist_plant)))}[{plant_dir}] | {(round(sqrt(self.vision.max_dist_meat)))}[{meat_dir}]", rpos.x, rpos.y
        #return f"{(round(sqrt(self.vision.max_dist)))}", rpos.x, rpos.y
        return f"T:{(round(sqrt(self.vision.max_dist)))} | E:{(round(sqrt(self.vision.max_dist_enemy)))} | P:{(round(sqrt(self.vision.max_dist_plant)))} | M:{(round(sqrt(self.vision.max_dist_meat)))}", rpos.x, rpos.y

    def update(self, dt: float, selected: Body):
        super().update(dt, selected)
        self.life_time += dt*0.1
        if self.running:
            self.hidding = False
            self.run_time -= dt
            if self.run_time < 0:
                self.run_time = 0
                self.running = False
        else:
            self.run_time += dt
            if self.run_time > cfg.RUN_TIME:
                self.run_time = cfg.RUN_TIME
        move = self.move(dt)
        self.calc_energy(dt, move)
        self.mem_time -= dt
        self.mem_time = clamp(self.mem_time, 0, cfg.MEM_TIME)
        if self.run_ref_time != 0.0:
            self.run_ref_time -= dt
            if self.run_ref_time < 0.0:
                self.run_ref_time = 0.0
        if self.hide_ref_time != 0.0:
            self.hide_ref_time -= dt
            if self.hide_ref_time < 0.0:
                self.hide_ref_time = 0.0

    def check_reproduction(self, dt) -> bool:
        self.reproduction_time -= dt
        if self.reproduction_time <= 0:
            self.reproduction_time = 0
            if self.energy >= (self.max_energy*(1-cfg.REP_ENERGY)):
                return True
        return False

    def update_detections(self, detections: list): 
        for detector in self.sensors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def reproduce(self, screen: Surface, space: Space):
        self.childs += 1
        x2: float=self.position.x+randint(-100, 100)
        y2: float=self.position.y+randint(-100, 100)
        x2 = clamp(x2, 50, cfg.WORLD[0]-50)
        y2 = clamp(y2, 50, cfg.WORLD[1]-50)
        x1: float=self.position.x
        y1: float=self.position.y
        pos = Vec2d(x1, y1)
        genome: dict=self.get_genome()
        genome['neuro'] = self.neuro.Replicate()
        self.reproduction_time = cfg.REP_TIME
        self.fitness += cfg.BORN2FIT
        self.energy -= self.energy*cfg.REP_ENERGY
        return (genome, pos)
      
    def move(self, dt: float) -> None:
        move = 0
        if self.running and not self.on_water:
           move = cfg.SPEED*self.speed*2
        elif self.on_water:
            move = cfg.SPEED*self.speed*self.moving*cfg.WATER_MOVE
        elif self.hidding:
            move = cfg.SPEED*self.speed*self.moving*0.1
        else:
            move = cfg.SPEED*self.speed*self.moving
        if move < 0:
            move = 0
        turn = self.turning*cfg.TURN*dt
        self.sensor_angle = (1-((self.output[3]+1)/2))*cfg.SENSOR_MAX_ANGLE
        self.angle = (self.angle+(turn))%(2*PI)
        self.velocity = (move*self.rotation_vector.x, move*self.rotation_vector.y)
        return abs(move)

    def calc_energy(self, dt: float, move: float):
        size_cost = self.size * cfg.SIZE_COST
        move_energy = move * cfg.MOVE_ENERGY * size_cost
        base_energy = cfg.BASE_ENERGY
        if self.running:
            move_energy *= cfg.RUN_COST
        rest_energy = self.power * cfg.POWER_COST
        if self.eating:
            rest_energy += cfg.EAT_ENG
        if self.attacking:
            rest_energy += cfg.ATK_ENG
        if self.on_water:
            base_energy += cfg.WATER_COST
        base_energy *= size_cost
        self.energy -= (base_energy + move_energy + rest_energy) * dt
        self.energy = clamp(self.energy, 0, self.max_energy)

    def get_input(self):
        input = []
        al, ar, ad, pl, pr, pd, ml, mr, md = self.vision.get_detection()
        #x = (self.position[0]-(cfg.WORLD[0]/2))/(cfg.WORLD[0]/2)
        #y = (self.position[1]-(cfg.WORLD[1]/2))/(cfg.WORLD[1]/2)
        eng = self.energy/self.max_energy
        input.append(self.collide_creature)
        input.append(self.collide_plant)
        input.append(self.collide_meat)
        #input.append(x)
        #input.append(y)
        input.append(eng)
        input.append(int(self.pain))
        input.append(al)
        input.append(ar)
        input.append(ad)
        input.append(pl)
        input.append(pr)
        input.append(pd)
        input.append(ml)
        input.append(mr)
        input.append(md)
        self.pain = False
        #self.reset_collisions()
        return input

    def analize(self):
        if self.mem_time <= 0:
            input = self.get_input()
            self.output = self.neuro.Calc(input)
            self.mem_time = cfg.MEM_TIME
            for o in range(len(self.output)):
                self.output[o] = clamp(self.output[o], 0, 1)
            self.moving = self.output[0]
            self.turning = self.output[2] - self.output[1]
            if self.output[3] >= 0.4:
                self.eating = True
            else:
                self.eating = False
            if self.output[4] >= 0.5:
                self.attacking = True
            else:
                self.attacking = False
            if self.output[5] >= 0.7 and not self.on_water:
                if not self.running and self.run_time >= int(cfg.RUN_TIME/2):
                    if self.run_ref_time == 0.0:
                        self.run_ref_time = 1.0
                        self.running = True
                    else:
                        self.running = False
                if self.running:
                    self.running = True
            else:
                self.running = False
        #if self.output[6] >= 0.7 and not self.running:
        #    if not self.hidding:
        #        if self.hide_ref_time == 0.0:
        #            self.hide_ref_time = 1.0
        #            self.hidding = True
        #        else:
        #            self.hidding = False
        #    else:
        #        self.hidding = True
        #else:
        #    self.hidding = False
        #    self.output[6] = 0
            
    def draw_energy_bar(self, screen: Surface, rx: int, ry: int):
        bar_red = Color(255, 0, 0)
        bar_green = Color(0, 255, 0)
        size = self.shape.radius
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(19), 1), bar_red)
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(20*(self.energy/self.max_energy)), 1), bar_green)
  
    def life2fit(self):
        self.fitness += self.life_time
        self.fitness = round(self.fitness)

    def kill(self, space: Space):
        to_kill = []
        to_kill.append(self.vision)
        for s in to_kill:
            space.remove(s)
        space.remove(self.shape)
        space.remove(self)

    def add_specie(self, name: str, generation: int, time: int):
        data = (name, generation, time)
        self.genealogy.append(data)

    def get_genome(self) -> dict:
        genome: dict = {}
        genome['name'] = copy(self.name)
        genome['gen'] = self.generation
        genome['food'] = self.food
        genome['size'] = self.size
        genome['mutations'] = self.mutations
        genome['fitness'] = self.fitness
        genome['power'] = self.power
        genome['speed'] = self.speed
        genome['color0'] = self._color0
        genome['color1'] = self._color1
        genome['color2'] = self._color2
        genome['color3'] = self._color3
        genome['neuro'] = self.neuro.Replicate()
        genome['signature'] = deepcopy(self.signature)
        genome['genealogy'] = copy(self.genealogy)
        return genome

    def similar(self, parent_genome: dict, treashold: float) -> bool:
        physionomy = []
        nodes = []
        links = []
        size_diff = abs(self.size-parent_genome['size'])
        mutations_diff = abs(self.mutations-parent_genome['mutations'])
        power_diff = abs(self.power-parent_genome['power'])
        food_diff = abs(self.food-parent_genome['food'])
        speed_diff = abs(self.speed-parent_genome['speed'])
        physionomy = mean([size_diff, power_diff,food_diff, speed_diff, mutations_diff])/10
        for node_sign in self.neuro.nodes:
            if not node_sign in parent_genome['neuro'].nodes:
                nodes.append(node_sign)
        for node_sign in parent_genome['neuro'].nodes:
            if not node_sign in self.neuro.nodes:
                nodes.append(node_sign)
        for link_sign in self.neuro.links:
            if not link_sign in parent_genome['neuro'].links:
                links.append(link_sign)
        for link_sign in parent_genome['neuro'].links:
            if not link_sign in self.neuro.links:
                links.append(link_sign)
        nodes_diff = len(nodes)/(len(self.neuro.nodes) + len(parent_genome['neuro'].nodes))
        links_diff = len(links)/(len(self.neuro.links) + len(parent_genome['neuro'].links))
        similar = 1 - mean([physionomy, nodes_diff, links_diff])
        if similar > treashold:
            return False
        else:
            return True

    def eat(self, energy: float):
        #energy *= self.meat/10
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.max_energy)

    def hit(self, dmg: float) -> bool:
        self.energy -= dmg
        self.energy = clamp(self.energy, 0, self.max_energy)
        self.pain = True
        self.color0=Color('red')
        if self.energy <= 0:
            return True
        return False

    def get_signature(self) -> list:
        signature: list=[]
        #signature.append([self.size, self.power, self.vege, self.meat])
        signature.append([self.size, self.power, self.food])
        links_keys: list=[]
        for link_key in self.neuro.links:
            links_keys.append(link_key)
        signature.append(links_keys)
        return signature

    def compare_signature(self, signature1: list, signature2: list, treashold: float) -> bool:
        fizjo1 = signature1[0]
        fizjo2 = signature2[0]
        neuro1 = signature1[1]
        neuro2 = signature2[1]
        fizjo_diff: list = []
        neuro_diff: int = 0
        for f in range(len(fizjo1)):
            diff = abs(fizjo1[f]-fizjo2[f])
            fizjo_diff.append(diff)
        for n1 in neuro1:
            if not n1 in neuro2:
                neuro_diff += 1
        for n2 in neuro2:
            if not n2 in neuro1:
                neuro_diff += 1
        mean_fizjo_diff = (mean(fizjo_diff))/10
        mean_neuro_diff = neuro_diff / ((len(neuro1) + len(neuro2))/2)
        diff = mean([mean_fizjo_diff, mean_neuro_diff])
        #log_to_file(f'diff: [{round(mean_fizjo_diff, 2)}] [{round(mean_neuro_diff, 2)}] [{round(diff, 2)}]', 'log.txt')
        if diff <= treashold:
            return True
        else:
            return False