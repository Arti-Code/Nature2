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

class Creature(Life):

    def __init__(self, screen: Surface, space: Space, time: int, collision_tag: int, position: Vec2d, genome: dict=None, color0: Color=Color('grey'), color1: Color=Color('skyblue'), color2: Color=Color('orange'), color3: Color=Color('red')):
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
        self.angle = random()*2*PI
        self.output = [0, 0, 0, 0, 0, 0, 0]
        self.generation = 0
        self.fitness = 0
        self.neuro = Network()
        self.normal: Vec2d=Vec2d(0, 0)
        self.signature: list=[]
        self.childs = 0
        self.kills = 0
        self.genealogy = []
        if genome == None:
            self.random_build(color0, color1, color2, color3, time)
            self.signature = self.get_signature()
        else:
            self.genome_build(genome)
            #msg: str=''
            if not self.compare_signature(self.get_signature(), genome['signature'], cfg.DIFF):
                self.signature = self.get_signature()
                self.name = modify_name(genome['name'])
                self.add_specie(self.name, self.generation, time)
        self.shape = Circle(self, self.size)
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        self.eye_colors = {}
        self.visual_range = cfg.VISUAL_RANGE
        self.sensors = []
        self.side_angle = 0
        sensors_angle = ((random()+1)/2)*(PI/1.5)
        self.sensors.append(Sensor(screen, self, 4, 0, cfg.SENSOR_RANGE))
        self.sensors.append(Sensor(screen, self, 4, sensors_angle, cfg.SENSOR_RANGE))
        self.sensors.append(Sensor(screen, self, 4, -sensors_angle, cfg.SENSOR_RANGE))
        self.mem_time = 0
        self.max_energy = self.size*cfg.SIZE2ENG
        self.reproduction_time = cfg.REP_TIME
        self.energy = self.max_energy
        self.water = self.max_energy
        for sensor in self.sensors:
           space.add(sensor.shape)
        self._move: float=0.0
        self._eat: bool=False
        self._attack: bool=False
        self._turn: float=0.0
        self.pain: bool=False
        self.run: bool=False
        self.life_time: float=0.0
        self.run_time = cfg.RUN_TIME
        self.hide = False
        self.on_water = (False, 0)
        #self.water_ahead = False

    def genome_build(self, genome: dict):
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
        self.neuro.Mutate(mutations_rate=self.mutations)
        self.signature = genome['signature']

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
        if self.hide:
            color0.a = 40
            color1.a = 40
            color2.a = 40
            a = 40
        else:
            color0.a = 255
            color1.a = 255
            color2.a = 255
            a = 255
        if selected == self:
            self.draw_detectors(screen=screen, rel_pos=rel_pos)
        for detector in self.sensors:
            detector.reset_data()
        gfxdraw.aacircle(screen, int(rx), int(ry), int(r), color0)
        gfxdraw.filled_circle(screen, int(rx), int(ry), int(r), color0)
        gfxdraw.aacircle(screen, int(rx), int(ry), int(r-1), self.color1)
        gfxdraw.filled_circle(screen, int(rx), int(ry), int(r-1), color1)
        if r > 2:
            x2 = round(rx + rot.x*(r/1.6))
            y2 = round(ry - rot.y*(r/1.6))
            #x3 = round(x - rot.x*(r/5))
            #y3 = round(y - rot.y*(r/5))
            r2 = round(r/2)
            #r3 = round(r/3)
            #h: int=self.food*10; s: int=100; l: int=50
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
            gfxdraw.aacircle(screen, int(x2), int(y2), int(r2), Color(r, g, b, a))    
            gfxdraw.filled_circle(screen, int(x2), int(y2), int(r2), Color(r, g, b, a))
            gfxdraw.aacircle(screen, int(rx), int(ry), int(r2), color2)
            gfxdraw.filled_circle(screen, int(rx), int(ry), int(r2), color2)
        self.color0 = self._color0
        self.draw_energy_bar(screen, rx, ry)
        self.draw_water_bar(screen, rx, ry)
        #self.draw_name(screen)
        #self.draw_normal(screen)
        return True

    def detect_water(self, screen: Surface) -> list:
        return self.sensors[0].get_water_detectors(screen)

    def draw_normal(self, screen):
        if self.normal != None:
            gfxdraw.line(screen, int(self.position.x), int(flipy(self.position.y)), int(self.position.x+self.normal.x*50), int(flipy(self.position.y+self.normal.y*50)), Color('yellow'))
            #self.normal = None

    def draw_detectors(self, screen, rel_pos: Vector2):
        first = True
        for detector in self.sensors:
            if self.water_ahead and first:
                detector.set_color('blue')
            detector.draw(screen=screen, rel_pos=rel_pos)
            first = False
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False
        self.collide_meat = False

    def draw_name(self, camera: Camera):
        rpos = camera.rel_pos(Vector2((self.position.x-20), flipy(self.position.y-14)))
        return self.name, rpos.x, rpos.y

    def update(self, dt: float, selected: Body):
        super().update(dt, selected)
        self.life_time += dt*0.1
        self.drink(dt) 
        if self.run:
            self.run_time -= dt
            if self.run_time < 0:
                self.run_time = 0
        else:
            self.run_time += dt
            if self.run_time > cfg.RUN_TIME:
                self.run_time = cfg.RUN_TIME
        move = self.move(dt)
        self.calc_energy(dt, move)
        self.mem_time -= dt
        self.mem_time = clamp(self.mem_time, 0, cfg.MEM_TIME)
        if self.hide:
            if self.run or self._move >= 0.2:
                self.hide = False
                self.output[5] = 0

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
        pos = Vec2d(x2, y2)
        genome: dict=self.get_genome()
        genome['neuro'] = self.neuro.Replicate()
        self.reproduction_time = cfg.REP_TIME
        self.fitness += cfg.BORN2FIT
        self.energy -= self.energy*cfg.REP_ENERGY
        return (genome, pos)
      
    def move(self, dt: float) -> None:
        move = cfg.SPEED*self.speed*self._move
        if self.run:
           move *= 1.5
        if move < 0:
            move = 0
        if self.on_water:
            move *= cfg.WATER_MOVE
        turn = self._turn*cfg.TURN*dt
        #sensor_turn = self.output[2]*cfg.SENSOR_SPEED*dt
        #sensor_angle = (PI*1.5)-(((self.output[2]+1)/2)*(PI*1.5))
        sensor_angle = ((self.output[2]+1)/2)*(PI/1.5)
        #sensor_angle = self.output[2]*(PI/2)
        self.angle = (self.angle+(turn))%(2*PI)
        self.velocity = (move*self.rotation_vector.x, move*self.rotation_vector.y)
        #self.sensors[1].rotate(sensor_turn, 0, PI/1.5)
        #self.sensors[2].rotate(-sensor_turn, -PI/1.5, 0)
        self.sensors[1].rotate_to(sensor_angle, 0, cfg.SENSOR_MAX_ANGLE, dt)
        self.sensors[2].rotate_to(-sensor_angle, -cfg.SENSOR_MAX_ANGLE, 0, dt)
        #for sensor in self.sensors:
        #    sensor.update()
        return abs(move)

    def calc_energy(self, dt: float, move: float):
        size_cost = self.size * cfg.SIZE_COST
        move_energy = move * cfg.MOVE_ENERGY * size_cost
        base_energy = cfg.BASE_ENERGY
        water_lost = cfg.WATER_NEEDS*size_cost
        if self.run:
            move_energy *= cfg.RUN_COST
        rest_energy = 0
        if self._eat:
            rest_energy += cfg.EAT_ENG
        if self._attack:
            rest_energy += cfg.ATK_ENG
        if self.on_water[0]:
            base_energy += cfg.WATER_COST * self.on_water[1]
        base_energy *= size_cost
        self.energy -= (base_energy + move_energy + rest_energy) * dt
        self.water -= water_lost * dt
        self.energy = clamp(self.energy, 0, self.max_energy)
        self.water = clamp(self.water, 0, self.max_energy)

    def drink(self, dt: float):
        if self.on_water:
            if self._eat:
                self.water += cfg.WATER*dt

    def get_input(self):
        input = []
        input.append(self.collide_creature)
        input.append(self.collide_plant)
        #input.append(self.collide_something)
        input.append(self.collide_meat)
        input.append(self.on_water[0])
        angle = self.angle/(2*PI)
        side_angle = self.sensors[1].angle/(cfg.SENSOR_MAX_ANGLE*2)
        #input.append(angle)
        input.append(side_angle)
        x = self.position[0]/cfg.WORLD[0]
        input.append(x)
        y = self.position[1]/cfg.WORLD[1]
        input.append(y)
        eng = self.energy/self.max_energy
        input.append(eng)
        for sensor in self.sensors:
            detected = []
            detected = sensor.get_input()
            e = detected[0]
            p = detected[1]
            #o = detected[2]
            m = detected[3]
            d = round(detected[4], 2)
            input.append(e)
            input.append(p)
            input.append(m)
            #input.append(o)
            input.append(d)
        input.append(self.water_ahead)
        input.append(int(self.pain))
        self.pain = False
        return input

    def analize(self):
        if self.mem_time <= 0:
            input = self.get_input()
            self.output = self.neuro.Calc(input)
            self.mem_time = cfg.MEM_TIME
            for o in range(len(self.output)):
                if self.output[o] < -1 or self.output[o] > 1:
                    self.output[o] = clamp(self.output[o], -1, 1)
        self._move = clamp(self.output[0], 0, 1)
        self._turn = self.output[1]
        if self.output[3] > 0:
            self._eat = True
        else:
            self._eat = False
        if self.output[4] > 0:
            self._attack = True
        else:
            self._attack = False
        if self.output[5] > 0 and self.run_time > 0 and self._move > 0 and not self.on_water:
            self.run = True
        else:
            self.run = False
        if self.output[6] > 0:
            self.hide = True
        else:
            self.hide = False
            self.output[5] = 0
            
    def draw_energy_bar(self, screen: Surface, rx: int, ry: int):
        bar_red = Color(255, 0, 0)
        bar_green = Color(0, 255, 0)
        size = self.shape.radius
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(19), 1), bar_red)
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(20*(self.energy/self.max_energy)), 1), bar_green)
    
    def draw_water_bar(self, screen: Surface, rx: int, ry: int):
        bar_blue = Color(0, 0, 255)
        bar_gray = Color(150, 150, 150)
        size = self.shape.radius
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+6), round(19), 1), bar_gray)
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+6), round(20*(self.water/self.max_energy)), 1), bar_blue)
    
    def kill(self, space: Space):
        to_kill = []
        for sensor in self.sensors:
            to_kill.append(sensor.shape)
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
        phisionomy = []
        nodes = []
        links = []
        size_diff = abs(self.size-parent_genome['size'])
        mutations_diff = abs(self.mutations-parent_genome['mutations'])
        power_diff = abs(self.power-parent_genome['power'])
        food_diff = abs(self.food-parent_genome['food'])
        speed_diff = abs(self.speed-parent_genome['speed'])
        phisionomy = mean([size_diff, power_diff,food_diff, speed_diff, mutations_diff])/10
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
        similar = 1 - mean([phisionomy, nodes_diff, links_diff])
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