from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from pygame.font import Font
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.life import Life
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor, PolySensor
from lib.net import Network
from lib.config import *
from lib.names import random_name


class Creature(Life):

    def __init__(self, screen: Surface, space: Space, sim: object, collision_tag: int, position: Vec2d, genome: dict=None, color0: Color=Color('blue'), color1: Color=Color('skyblue'), color2: Color=Color('orange'), color3: Color=Color('red')):
        super().__init__(screen=screen, space=space, owner=sim, collision_tag=collision_tag, position=position)
        self.angle = random()*2*PI
        self.output = [0, 0, 0]
        self.generation = 0
        self.fitness = 0
        self.neuro = Network()
        self.normal: Vec2d=None
        if genome == None:
            self.color0 = color0
            self.color1 = color1
            self.color2 = color2
            self.color3 = color3
            self._color0 = color0
            self._color1 = color1
            self._color2 = color2
            self._color3 = color3
            self.meat = randint(1, 10)
            self.vege = randint(1, 10)
            self.power = randint(1, 10)
            self.size = randint(CREATURE_MIN_SIZE, CREATURE_MAX_SIZE)
            self.neuro.BuildRandom([33, 0, 0, 0, 0, 0, 3], 0.3)
            self.name = random_name(4, True)
        else:
            self.color0 = Color(genome['color0'][0], genome['color0'][1], genome['color0'][2], genome['color0'][3])
            self.color1 = Color(genome['color1'][0], genome['color1'][1], genome['color1'][2], genome['color1'][3])
            self.color2 = Color(genome['color2'][0], genome['color2'][1], genome['color2'][2], genome['color2'][3])
            self.color3 = Color(genome['color3'][0], genome['color3'][1], genome['color3'][2], genome['color3'][3])
            self._color0 = self.color0
            self._color1 = self.color1
            self._color2 = self.color2
            self._color3 = self.color3
            self.neuro = genome['neuro']
            self.neuro.Mutate()
            self.size = genome['size'] + randint(-1, 1)
            self.meat = genome['meat'] + randint(-1, 1)
            self.vege = genome['vege'] + randint(-1, 1)
            self.power = genome['power'] + randint(-1, 1)
            self.meat = clamp(self.meat, 1, 10)
            self.size = clamp(self.size, CREATURE_MIN_SIZE, CREATURE_MAX_SIZE)
            self.vege = clamp(self.vege, 1, 10)
            self.power = clamp(self.power, 1, 10)
            self.generation = genome['gen']+1
            self.name = genome['name']
        self.shape = Circle(self, self.size)
        self.shape.collision_type = collision_tag
        space.add(self.shape)
        self.eye_colors = {}
        self.visual_range = VISUAL_RANGE
        self.sensors = []
        self.side_angle = 0
        self.sensors.append(Sensor(screen, self, 4, 0, 220))
        self.sensors.append(Sensor(screen, self, 4, SENSOR_MAX_ANGLE, 250))
        self.sensors.append(Sensor(screen, self, 4, -SENSOR_MAX_ANGLE, 250))
        self.mem_time = 0
        self.max_energy = self.size*SIZE2ENG
        self.reproduction_time = REP_TIME
        self.energy = self.max_energy
        for sensor in self.sensors:
            space.add(sensor.shape)
        #self.base_color0 = self.color0

    def draw(self, screen: Surface, selected: Body):
        super().draw(screen, selected)
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        rot = self.rotation_vector
        gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r), self.color0)
        gfxdraw.filled_circle(screen, int(x), flipy(int(y)), int(r-2), self.color1)
        gfxdraw.filled_circle(screen, int(x), flipy(int(y)), 2, self.color2)
        if r > 2:
            x2 = round(x + rot.x*(r-1))
            y2 = round(y + rot.y*(r-1))
            r2 = ceil(r/4)
            r: int; g: int; b: int
            if self.meat >= self.vege:
                r = round(225*(self.meat/(self.meat+self.vege)))
                g = round(225*(self.vege/(self.meat+self.vege)))
                b = 0
            else:
                r = round(225*(self.meat/(self.meat+self.vege)))
                g = round(225*(self.vege/(self.meat+self.vege)))
                b = 0
            gfxdraw.filled_circle(screen, x2, flipy(y2), r2, Color(r, g, b))
        self.color0 = self._color0
        self.draw_energy_bar(screen, int(x), flipy(int(y)))
        #self.draw_name(screen)
        #self.draw_normal(screen)

    def draw_normal(self, screen):
        if self.normal != None:
            gfxdraw.line(screen, int(self.position.x), int(flipy(self.position.y)), int(self.position.x+self.normal.x*50), int(flipy(self.position.y+self.normal.y*50)), Color('yellow'))
            #self.normal = None

    def draw_detectors(self, screen):
        for detector in self.sensors:
            detector.draw(screen)
            detector.reset_data()
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False
        self.collide_meat = False

    def draw_name(self):
        return self.name, self.position.x-20, flipy(self.position.y-14)

    def update(self, screen: Surface, space: Space, dt:float):
        move = self.move(dt)
        self.calc_energy(dt, move)
        self.mem_time -= 1/dt
        self.mem_time = clamp(self.mem_time, 0, MEM_TIME)

    def check_reproduction(self, dt) -> bool:
        self.reproduction_time -= 1/dt
        if self.reproduction_time <= 0:
            self.reproduction_time = 0
            if self.energy >= (self.max_energy*(1-REP_ENERGY)):
                return True
        return False

    def update_detections(self, detections: list): 
        for detector in self.sensors:
            if detector.shape in detections:
                detector.set_color(Color('red'))
            else:
                detector.set_color(Color('white'))

    def reproduce(self, screen: Surface, space: Space):
        x2: float=self.position.x+randint(-100, 100)
        y2: float=self.position.y+randint(-100, 100)
        x2 = clamp(x2, 50, WORLD[0]-50)
        y2 = clamp(y2, 50, WORLD[1]-50)
        pos = Vec2d(x2, y2)
        genome: dict=self.get_genome()
        genome['neuro'] = self.neuro.Replicate()
        self.reproduction_time = REP_TIME
        return (genome, pos)
      
    def move(self, dt: float) -> None:
        move = ((self.output[0]+1)/2)*SPEED/dt
        turn = self.output[1]*TURN/dt
        sensor_turn = self.output[2]*SENSOR_SPEED/dt
        self.angle = (self.angle+(turn))%(2*PI)
        self.velocity = (move*self.rotation_vector.x, move*self.rotation_vector.y)
        self.sensors[1].rotate(sensor_turn, 0, PI/1.5)
        self.sensors[2].rotate(-sensor_turn, -PI/1.5, 0)
        return abs(move)*dt

    def calc_energy(self, dt: float, move: float):
        base_energy = BASE_ENERGY * dt
        move_energy = move * MOVE_ENERGY * dt
        self.energy -= (base_energy + move_energy) * self.size * SIZE_COST
        self.energy = clamp(self.energy, 0, self.max_energy)

    def get_input(self):
        input = []
        input.append(self.collide_creature)
        input.append(self.collide_plant)
        input.append(self.collide_something)
        input.append(self.collide_meat)
        angle = self.angle/(2*PI)
        side_angle = self.sensors[1].angle/(SENSOR_MAX_ANGLE*2)
        input.append(angle)
        input.append(side_angle)
        x = self.position[0]/WORLD[0]
        input.append(x)
        y = self.position[1]/WORLD[1]
        input.append(y)
        eng = self.energy/self.max_energy
        input.append(eng)
        for sensor in self.sensors:
            e, d, a, p, pd, pa, o, od, oa, m, md, ma = sensor.get_input()
            pd = round(pd, 3)
            od = round(od, 3)
            md = round(md, 3)
            input.append(e)
            input.append(d)
            #input.append(a)
            input.append(p)
            input.append(pd)
            #input.append(pa)
            input.append(o)
            input.append(od)
            #input.append(oa)
            input.append(m)
            input.append(md)
        return input

    def analize(self):
        if self.mem_time <= 0:
            input = self.get_input()
            self.output = self.neuro.Calc(input)
            self.mem_time = MEM_TIME
        #for sensor in self.sensors:
        #    sensor.reset_data()
            
    def draw_energy_bar(self, screen: Surface, rx: int, ry: int):
        bar_red = Color(255, 0, 0)
        bar_green = Color(0, 255, 0)
        size = self.shape.radius
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(19), 1), bar_red)
        gfxdraw.box(screen, Rect(rx-round(10), ry+round(size+3), round(20*(self.energy/self.max_energy)), 1), bar_green)

    def kill(self, space: Space):
        to_kill = []
        for sensor in self.sensors:
            to_kill.append(sensor.shape)
        for s in to_kill:
            space.remove(s)
        space.remove(self.shape)
        space.remove(self)

    def get_genome(self) -> dict:
        genome: dict = {}
        genome['name'] = copy(self.name)
        genome['gen'] = self.generation
        genome['meat'] = self.meat
        genome['vege'] = self.vege
        genome['size'] = self.size
        genome['fitness'] = self.fitness
        genome['power'] = self.power
        genome['color0'] = self._color0
        genome['color1'] = self._color1
        genome['color2'] = self._color2
        genome['color3'] = self._color3
        genome['neuro'] = self.neuro.Replicate()
        return genome

    def eat(self, energy: float):
        #energy *= self.meat/10
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.max_energy)