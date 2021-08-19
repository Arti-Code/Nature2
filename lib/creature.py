from copy import copy, deepcopy
from random import random, randint
from math import sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.life import Life
from lib.math2 import flipy, ang2vec, ang2vec2, clamp
from lib.sensor import Sensor, PolySensor
from lib.net import Network
from lib.config import *


class Creature(Life):

    def __init__(self, screen: Surface, space: Space, sim: object, collision_tag: int, world_size: Vec2d, size: int, color0: Color, color1: Color, color2: Color, color3: Color, angle: float=None, visual_range: int=180, position: Vec2d=None, genome: dict=None):
        super().__init__(screen=screen, space=space, owner=sim, collision_tag=collision_tag, world_size=world_size, size=size, color0=color0, color1=color1, position=position)
        if angle:
            self.angle = angle
        else:
            self.angle = random()*2*PI
        self.output = [0, 0, 0]
        self.color2 = color2
        self.color3 = color3
        self.generation = 0
        self.fitness = 0
        self.neuro = Network()
        if genome == None:
            self.meat = randint(1, 10)
            self.vege = randint(1, 10)
            self.power = randint(1, 10)
            self.size = randint(CREATURE_MIN_SIZE, CREATURE_MAX_SIZE)
            self.neuro.BuildRandom([26, 0, 0, 0, 0, 0, 3], 0.3)
        else:
            self.neuro = genome['neuro']
            self.neuro.Mutate()
            self.meat = genome.meat + randint(-1, 1)
            self.vege = genome.vege + randint(-1, 1)
            self.power = genome.power + randint(-1, 1)
            self.meat = clamp(self.meat, 1, 10)
            self.vege = clamp(self.vege, 1, 10)
            self.power = clamp(self.power, 1, 10)
            self.generation = genome['generation']+1
        self.eye_colors = {}
        self.visual_range = visual_range
        self.sensors = []
        self.reproduction_time = REPRODUCTION_TIME
        self.side_angle = 0
        self.sensors.append(Sensor(screen, self, 4, 0, 220))
        self.sensors.append(Sensor(screen, self, 4, SENSOR_MAX_ANGLE, 250))
        self.sensors.append(Sensor(screen, self, 4, -SENSOR_MAX_ANGLE, 250))
        self.mem_time = 0
        self.name = 'creature'
        for sensor in self.sensors:
            space.add(sensor.shape)

    def draw(self, screen: Surface, selected: Body):
        super().draw(screen, selected)
        x = self.position.x; y = self.position.y
        r = self.shape.radius
        rot = self.rotation_vector
        if r > 2:
            x2 = round(x + rot.x*(r-1))
            y2 = round(y + rot.y*(r-1))
            r2 = ceil(r/4)
            gfxdraw.filled_circle(screen, x2, flipy(y2), r2, self.color2)
        self.color0 = self.base_color0
        self.draw_energy_bar(screen, int(x), flipy(int(y)))

    def draw_detectors(self, screen):
        for detector in self.sensors:
            detector.draw(screen)
            detector.reset_data()
        self.collide_creature = False
        self.collide_plant = False
        self.collide_something = False

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
        pos = Vec2d(self.position.x+randint(-100, 100), self.position.y+randint(-100, 100))
        genome: dict=self.get_genome()
        genome['neuro'] = self.neuro.Replicate()
        self.reproduction_time = REPRODUCTION_TIME
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
        self.energy -= (base_energy + move_energy)
        self.energy = clamp(self.energy, 0, self.max_energy)

    def get_input(self):
        input = []
        input.append(self.collide_creature)
        input.append(self.collide_plant)
        input.append(self.collide_something)
        angle = self.angle/(2*PI)
        side_angle = self.sensors[1].angle/(SENSOR_MAX_ANGLE*2)
        input.append(angle)
        input.append(side_angle)
        x = self.position[0]/self.world_size[0]
        input.append(x)
        y = self.position[1]/self.world_size[1]
        input.append(y)
        eng = self.energy/self.max_energy
        input.append(eng)
        for sensor in self.sensors:
            e, d, a, p, pd, pa, o, od, oa = sensor.get_input()
            d = round(d, 3)
            #a = round(a%PI, 3)
            pd = round(pd, 3)
            #pa = round(pa%PI, 3)
            od = round(od, 3)
            #oa = round(oa%PI, 3)
            input.append(e)
            input.append(d)
            #input.append(a)
            input.append(p)
            input.append(pd)
            #input.append(pa)
            input.append(o)
            input.append(od)
            #input.append(oa)
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
        genome['color0'] = self.color0
        genome['color1'] = self.color1
        genome['color2'] = self.color2
        genome['color3'] = self.color3
        genome['neuro'] = self.neuro.Replicate()
        return genome

    def eat(self, energy: float):
        self.energy += energy
        self.energy = clamp(self.energy, 0, self.max_energy)