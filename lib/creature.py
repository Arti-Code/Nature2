#from cmath import cos, sin
from copy import copy, deepcopy
from math import pi as PI
from math import sqrt, sin, cos
from random import randint, random, choice
from statistics import mean

import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface
from pygame.math import Vector2
from pymunk import Body, Circle, Space, Vec2d

from lib.config import cfg
from lib.camera import Camera
from lib.life import Life
from lib.math2 import clamp, flipy
from lib.net import Network
from lib.species import modify_name, random_name
from lib.vision import Vision
from lib.utils import Timer
from lib.spike import Spike


class Creature(Life):

    ATTACK_EYES: Color=Color('red')
    EAT_EYES: Color=Color('yellow')
    NORMAL_EYES: Color=Color('skyblue')
    HIDED_EYES: Color=Color(175,175,175,50)
    STUNT_EYES: Color=Color('limegreen')
    SPIKES_NUM: list[int] = [0, 1, 1, 1, 3, 5, 7, 9, 13, 15]

    def __init__(self, screen: Surface, space: Space, time: int, collision_tag: int, position: Vec2d, genome: dict=None, color0: Color=Color('grey'), color1: Color=Color('skyblue'), color2: Color=Color('orange'), color3: Color=Color('red')):
        super().__init__(screen=screen, space=space, collision_tag=collision_tag, position=position)
        self.angle = random()*2*PI
        self.output: list[float] = [0, 0, 0, 0, 0, 0]
        self.generation = 0
        self.fitness = 0
        self.spike_num: int = 1
        self.neuro = Network()
        self.normal: Vec2d=Vec2d(0, 0)
        self.signature: list=[]
        self.childs = 0
        self.kills = 0
        self.genealogy: list[(str, int, int)] = []
        self.mutations_num = [(0, 0), (0, 0)]
        self.open_yaw: bool=True
        if genome == None:
            self.random_build(color0, color1, color2, color3, time)
            self.signature = self.get_signature()
        else:
            self.mutations_num = self.genome_build(genome, time)
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
        self.rng = int(cfg.SENSOR_RANGE*0.4 + cfg.SENSOR_RANGE*(1-(self.eyes/10))*0.6)
        self.vision: Vision = Vision(self, self.rng, cfg.SENSOR_MAX_ANGLE*(self.eyes/10), (0.0, 0.0), "vision")
        space.add(self.vision)
        self.mem_time = 0
        self.max_energy = self.size*cfg.SIZE2ENG
        self.reproduction_time = ((random()*2)-1)*cfg.REP_TIME*0.33+cfg.REP_TIME
        self.energy = self.max_energy
        self.moving: float=0.0
        self.eating: bool=False
        self.attacking: bool=False
        self.turning: float=0.0
        self.pain: bool=False
        self.running: bool=False
        self.life_time: float=0.0
        self.hide_time: float=0.0
        self.run_time = random()*cfg.RUN_TIME
        self.hidding: bool=False
        self.hide_ref_time = 0.0
        self.run_ref_time = 0.0
        self.neuro.CalcNodeMutMod()
        self.rock_vec: Vec2d=None
        self.rock_dist = 0
        self.eng_lost = {'basic': 0.0, 'move': 0.0, 'neuro': 0.0, 'other': 0}
        self.ahead: Vec2d
        self.update_orientation()
        self.collide_time: bool=False
        self.create_timers()
        self.shooting: bool=False
        self.stunt: bool = False
        self.spikes_ready: bool = True
        self.check_edges_needed: bool = False
        if len(self.genealogy) == 0:
            self.genealogy.append((self.name, self.generation, time))
        self.calc_color()
        self.brain_just_used = False

    def create_timers(self):
        self.timer: dict[Timer] = {}
        collide_timer = Timer(random()*cfg.COLLIDE_TIME, False, True, "collide", True)
        stunt_timer = Timer(1, True, False, "stunt", False)
        spikes_reload = Timer(8, False, False, "spikes_reload", False)
        edges = Timer(2, False, True, "edges", True)
        self.timer["collisions"] = collide_timer
        self.timer["stunt"] = stunt_timer
        self.timer["spikes_reload"] = spikes_reload
        self.timer["edges"] = edges

    def update_timers(self, dt: float):
        for (k, t) in self.timer.items():
            if t.timeout(dt):
                if t.label == "collide":
                    self.collide_time=True
                elif t.label == "stunt":
                    self.stunt = False
                elif t.label == "spikes_reload":
                    self.spikes_ready = True
                elif t.label == "edges":
                    self.check_edges_needed = True

    def genome_build(self, genome: dict, time: int) -> list[tuple]:
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
        self.eyes = genome['eyes'] + randint(-1, 1)
        self.speed = genome['speed'] + randint(-1, 1)
        self.size = clamp(self.size, cfg.CREATURE_MIN_SIZE, cfg.CREATURE_MAX_SIZE)
        self.mutations = clamp(self.mutations, 1, 10)
        self.power = clamp(self.power, 1, 10)
        self.food = clamp(self.food, 1, 10)
        self.eyes = clamp(self.eyes, 1, 10)
        self.speed = clamp(self.speed, 1, 10)
        self.generation = genome['gen']+1
        self.name = genome['name']
        self.genealogy = genome['genealogy']
        self.first_one = genome['first_one']
        mutations = self.neuro.Mutate(self.mutations)
        self.nodes_num = self.neuro.GetNodesNum()
        self.links_num = self.neuro.GetLinksNum()
        self.signature = genome['signature']
        self.spike_num = genome['spike_num']
        if random() <= 0.1:
            self.spike_num = self.rand_spike_num()
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
        self.mutations = randint(1, 10)
        self.power = randint(1, 10)
        self.eyes = randint(1, 10)
        self.speed = randint(1, 10)
        self.spike_num = self.rand_spike_num()
        self.size = randint(cfg.CREATURE_MIN_SIZE, cfg.CREATURE_MAX_SIZE)
        self.neuro.BuildRandom(cfg.NET, cfg.LINKS_RATE)
        self.nodes_num = self.neuro.GetNodesNum()
        self.links_num = self.neuro.GetLinksNum()
        self.name = random_name(3, True)
        self.first_one = self.name
        self.add_specie(self.name, self.generation, time)

    def rand_spike_num(self) -> int:
        return choice(self.SPIKES_NUM)

    def update_orientation(self):
        self.ahead = self.position+self.rotation_vector*self.size*1.2

    def calc_color(self):
        self.r: int; self.g: int; self.b: int
        if self.food >= 6:
            self.r = round(25.5*self.food)
            self.g = round(255-25.5*self.food)
            self.b = 0
            self.r +=50
            self.g -=50
            self.r = clamp(self.r, 0, 255)
            self.g = clamp(self.g, 0, 255)
        else:
            self.r = round(25.5*(self.food-1))
            self.g = round(255-25.5*(self.food+1))
            self.b = 0
            self.r -=50
            self.g +=50
            self.r = clamp(self.r, 0, 255)
            self.g = clamp(self.g, 0, 255)

    def draw(self, screen: Surface, camera: Camera, selected: Body) -> bool:
        x = self.position.x; y = flipy(self.position.y)
        size = round(self.shape.radius / camera.scale)
        rect = Rect(x-size, y-size, 2*size, 2*size)
        if not camera.rect_on_screen(rect):
            return False
        rel_pos = camera.rel_pos(Vector2(x, y))
        self.rel_pos = rel_pos
        self.rel_size = size
        rx = round(rel_pos.x)
        ry = round(rel_pos.y)
        super().draw(screen, camera, selected)
        rot = self.rotation_vector
        color0: Color; color1: Color; color2: Color; 
        color0 = self.color0
        color1 = self.color1
        color2 = self.color2
        if self.stunt:
            color2 = Color(100, 100, 100)  
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
        self.draw_yaw(screen, rel_pos, size, self.open_yaw)
        gfxdraw.aacircle(screen, rx, ry, size, color2)
        gfxdraw.filled_circle(screen, rx, ry, size, color2)
        if self.running:
            shadow = color2
            shadow.a = 80
            for i in range(3):
                sx = round(rx-(rot.x*size*(0.8*(i+1))))
                sy = round(ry-(rot.y*size*(0.8*(i+1))))
                gfxdraw.aacircle(screen, sx, sy, size, shadow)
                gfxdraw.filled_circle(screen, sx, sy, size, shadow)
                gfxdraw.aacircle(screen, sx, sy, size-1, shadow)
                gfxdraw.filled_circle(screen, sx, sy, size-1, shadow)
        if size > 2:
            r2 = round(size/2)
        else:
            r2 = size
        r: int=self.r; g: int=self.g; b: int=self.b
        if self.stunt:
            gfxdraw.aacircle(screen, rx, ry, r2, Color(50, 50, 50, a))
            gfxdraw.filled_circle(screen, rx, ry, r2, Color(50, 50, 50, a))
        else:
            gfxdraw.aacircle(screen, rx, ry, r2, Color(r, g, b, a))
            gfxdraw.filled_circle(screen, rx, ry, r2, Color(r, g, b, a))
        eyes_color: Color=self.NORMAL_EYES
        if self.stunt:
            eyes_color = self.STUNT_EYES
        elif self.hidding:
            eyes_color = self.HIDED_EYES
        elif self.attacking:
            eyes_color=self.ATTACK_EYES
        elif self.eating:
            eyes_color=self.EAT_EYES
        self.vision.draw(screen=screen, camera=camera, rel_position=rel_pos, selected=marked, eye_color=eyes_color)
        self.color0 = self._color0
        self.draw_energy_bar(screen, rx, ry, size)
        return True

    def draw_normal(self, screen):
        if self.normal != None:
            gfxdraw.line(screen, int(self.position.x), int(flipy(self.position.y)), int(self.position.x+self.normal.x*50), int(flipy(self.position.y+self.normal.y*50)), Color('yellow'))

    def draw_detectors(self, screen, rel_pos: Vector2):
        for detector in self.sensors:
            detector.draw(screen=screen, rel_pos=rel_pos)
        self.collide_creature = False
        self.collide_plant = False
        self.collide_meat = False

    def reset_collisions(self):
        self.collide_creature = False
        self.collide_plant = False
        self.collide_meat = False
        self.border = False
        
    def draw_name(self, camera: Camera):
        #return self.name+"("+str(round(self.timer['test'].time))+")", self.rel_pos.x-14, self.rel_pos.y+self.rel_size+6
        return self.name, self.rel_pos.x-14, self.rel_pos.y+self.rel_size+6

    def draw_dist(self, camera: Camera):
        rpos = camera.rel_pos(Vector2((self.position.x-50), flipy(self.position.y+30)))
        return f"T:{(round(sqrt(self.vision.max_dist)))} | E:{(round(sqrt(self.vision.max_dist_enemy)))} | P:{(round(sqrt(self.vision.max_dist_plant)))} | M:{(round(sqrt(self.vision.max_dist_meat)))}", rpos.x, rpos.y

    def draw_yaw(self, screen: Surface, pos: Vector2, size: float, open: bool=True):
        if size <= 3:
            return
        s: float = size/2
        f: float = self.angle
        n = 24-open*14
        a = 0
        d: float = 2*PI/n
        cv: Vector2=self.rotation_vector
        x0=pos.x + cv.x*size
        y0=pos.y + cv.y*size
        points: list[tuple]=[]
        for i in range(n):
            if i == 0:
                x = x0; y = y0
                points.append((x, y))
                continue
            a = f+d*i
            x=x0+(cos(a)*s)
            y=y0+(sin(a)*s)
            points.append((x, y))
        alfa: int=255
        if self.hidding:
            alfa=25
        color: Color=Color(150,150,150,alfa)
        gfxdraw.aapolygon(screen, points, color)
        gfxdraw.filled_polygon(screen, points, color)

    def update(self, dt: float, selected: Body):
        #self.brain_just_used = False
        super().update(dt, selected)
        if self.collide_time:
            self.collide_time = False
        self.update_timers(dt)
        if random() <= 0.01:
            self.open_yaw = not self.open_yaw
        
        if self.hidding:
            self.life_time += dt*0.1*cfg.HIDE_MOD
            self.hide_time += dt*0.1
        else:
            self.life_time += dt*0.1

        if self.running:
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
        if self.stunt or self.hidding:
            return False

        self.reproduction_time -= dt

        if self.reproduction_time <= 0:
            self.reproduction_time = 0
            if self.energy >= (self.max_energy*cfg.REP_ENERGY*2.5):
                return True
        return False

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
        self.energy -= self.max_energy*cfg.REP_ENERGY
        return (genome, pos)
      
    def move(self, dt: float) -> None:
        if self.stunt:
            self.velocity = (0, 0)
            return 0
        move = 0
        speed = cfg.SPEED*((self.speed*2)+(cfg.CREATURE_MAX_SIZE-self.size))/3
        if self.running:
           move = speed*2
        else:
            move = speed*self.moving
        if move < 0:
            move = 0
        turn = self.turning*cfg.TURN*dt
        self.angle = (self.angle+(turn))%(2*PI)
        self.velocity = (move*self.rotation_vector.x, move*self.rotation_vector.y)
        return abs(move)

    def calc_energy(self, dt: float, move: float):
        size_cost = self.size * cfg.SIZE_COST
        move_energy = move * cfg.MOVE_ENERGY * size_cost
        base_energy = cfg.BASE_ENERGY * size_cost
        neuro_energy = (self.nodes_num+self.links_num)*cfg.NEURO_COST
        if self.running:
            move_energy *= cfg.RUN_COST
        rest_energy = self.power * cfg.POWER_COST
        if self.eating:
            rest_energy += cfg.EAT_ENG
        if self.attacking:
            rest_energy += cfg.ATK_ENG
        rest_energy *= size_cost
        if self.hidding:
            base_energy*=cfg.HIDE_MOD; move_energy*=cfg.HIDE_MOD; rest_energy*=cfg.HIDE_MOD; neuro_energy*=cfg.HIDE_MOD
        total_eng_cost = base_energy + move_energy + rest_energy + neuro_energy
        self.eng_lost = {'basic': base_energy, 'move': move_energy, 'neuro': neuro_energy, 'other': rest_energy, 'velocity': move}
        self.energy -= total_eng_cost * dt
        self.energy = clamp(self.energy, 0, self.max_energy)

    def get_input(self):
        input = []
        ar, ad, af, aw, pr, pd, mr, md, rr, rd = self.vision.get_detection()
        eng = self.energy/self.max_energy
        dng = 0.0
        if aw != 0:
            pwr = self.size+self.power+(self.attacking*10)
            dng = clamp((aw-pwr)/30, -1, 1)
        input.append(self.collide_creature)
        input.append(self.collide_plant)
        input.append(self.collide_meat)
        input.append(eng)
        input.append(int(self.pain))
        input.append(ar)
        input.append(ad)
        input.append(af)
        input.append(dng)
        input.append(pr)
        input.append(pd)
        input.append(mr)
        input.append(md)
        input.append(rr)
        input.append(rd)
        #input.append(int(self.border))
        self.pain = False
        self.reset_collisions()
        return input

    def analize(self):
        if self.mem_time <= 0 and not self.stunt:
            if not self.vision.new_observation():
                self.update_orientation()
                return False
            input = self.get_input()
            self.vision.reset_observation()
            self.output = self.neuro.Calc(input)
            self.brain_just_used = True
            self.mem_time = cfg.MEM_TIME
            for o in range(len(self.output)):
                if o == 1:
                    self.output[o] = clamp(self.output[1], -1, 1)
                else:
                    self.output[o] = clamp(self.output[o], 0, 1)
            self.moving = self.output[0]
            self.turning = self.output[1]
            self.eating = False
            self.attacking = False
            if self.output[2] > self.output[3] and self.output[2] >= 0.2:
                self.eating = True
            elif self.output[3] > self.output[2] and self.output[3] >= 0.2:
                self.attacking = True
            if self.output[0] >= 0.9:
                if not self.running and self.run_time >= int(cfg.RUN_TIME/2):
                    if self.run_ref_time == 0.0:
                        self.run_ref_time = 1.0
                        self.running = True
                    else:
                        self.running = False
            else:
                self.running = False
            if self.output[4] >= 0.5 and self.moving <= cfg.HIDE_SPEED and not self.attacking and not self.eating:
                self.hidding = True
                #r=self.rng*cfg.HIDE_MOD
                #self.vision.change_range(round(r))
            else:
                self.hidding = False
                #self.vision.change_range(self.rng)
            if self.output[5] >= 0.9:
                self.shooting = True
            else:
                self.shooting = False
            return True
        else:
            return False

    def draw_energy_bar(self, screen: Surface, rx: int, ry: int, rel_size: int):
        bar_red = Color(255, 0, 0)
        bar_green = Color(0, 255, 0)
        gfxdraw.box(screen, Rect(rx-10, ry+rel_size+5, 20, 1), bar_red)
        gfxdraw.box(screen, Rect(rx-10, ry+rel_size+5, round(20*(self.energy/self.max_energy)), 1), bar_green)
  
    def life2fit(self):
        #self.fitness += self.life_time
        #self.fitness += (self.life_time-self.hide_time)
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
        if len(self.genealogy) == 0:
            self.genealogy.append(data)
        elif data[0] != self.genealogy[len(self.genealogy)-1][0]:
            self.genealogy.append(data)
        while len(self.genealogy) > cfg.GENERATIONS_NUMBER:
            self.genealogy.pop(0)

    def get_genome(self) -> dict:
        genome: dict = {}
        genome['name'] = copy(self.name)
        genome['gen'] = self.generation
        genome['food'] = self.food
        genome['size'] = self.size
        genome['mutations'] = self.mutations
        genome['fitness'] = self.fitness
        genome['power'] = self.power
        genome['eyes'] = self.eyes
        genome['speed'] = self.speed
        genome['color0'] = self._color0
        genome['color1'] = self._color1
        genome['color2'] = self._color2
        genome['color3'] = self._color3
        genome['neuro'] = self.neuro.Replicate()
        genome['signature'] = deepcopy(self.signature)
        genome['genealogy'] = copy(self.genealogy)
        genome['first_one'] = copy(self.first_one)
        genome['spike_num'] = self.spike_num
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
        eyes_diff = abs(self.eyes-parent_genome['eyes'])
        physionomy = mean([size_diff, power_diff,food_diff, speed_diff, mutations_diff, eyes_diff])/10
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
        if self.stunt:
            return
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
        signature.append([self.size, self.power, self.food, self.eyes, self.speed, self.mutations])
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
        for f in range(min([len(fizjo1), len(fizjo2)])):
            diff = abs(fizjo1[f]-fizjo2[f])
            fizjo_diff.append(diff)
        for n1 in neuro1:
            if not n1 in neuro2:
                neuro_diff += 1
        for n2 in neuro2:
            if not n2 in neuro1:
                neuro_diff += 1
        mean_fizjo_diff = (mean(fizjo_diff))/10
        sum_len = (len(neuro1) + len(neuro2))
        mean_neuro_diff = 0.0
        if sum_len != 0:
            mean_neuro_diff = neuro_diff / (sum_len/2)
        diff = mean([mean_fizjo_diff, mean_neuro_diff])
        if diff <= treashold:
            return True
        else:
            return False

    def is_shooting(self, space: Space):
        if self.spike_num==0 or not self.spikes_ready:
            self.shooting = False
            return False
        if self.shooting and not self.stunt:
            self.spikes_ready = False
            self.timer["spikes_reload"].restart()
            self.shooting = False
            self.energy -= self.power*cfg.SPIKE_ENG
            num = self.spike_num
            spikes: list[Spike] = [] 
            s = (2 * PI) / num
            for n in range(num):
                a = self.angle + n*s
                pos = self.position + Vec2d(cos(a), sin(a))*self.size*1.1
                spike: Spike=Spike(space, self, pos, 3*self.power/num, a, 2.0/num)
                spikes.append(spike)
            return spikes
        else:
            return False