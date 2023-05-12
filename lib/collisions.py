from random import randint

from turtle import Vec2D

from pymunk import SegmentQueryInfo, Space, Arbiter, Vec2d, ShapeFilter

from pygame import Color

from lib.config import *

from lib.vision import Target, TARGET_TYPE

from lib.rock import Rock

from lib.creature import Creature

from lib.plant import Plant

from lib.spike import Spike


def line_of_sight(space: Space, start_vec: Vec2d, end_vec: Vec2d, filter: ShapeFilter) -> bool:

    query: SegmentQueryInfo=space.segment_query_first(start_vec, end_vec, 1.0, filter)

    if query == None:

        return True

    elif not isinstance(query.shape.body, Rock):

        return True

    else:

        return False


def diet(food: int, mod: float) -> float:

    return pow(food, 2) * mod


def set_collision_calls(space: Space, dt: float, creatures_num: int):

# 2: body | 8: rock | 4: sensor | 6: plant | 12: new_plant | 16: eye | 10: meat | 14: water | 18: area
    

    creature_collisions = space.add_collision_handler(2, 2)

    creature_collisions.pre_solve = process_creatures_collisions

    creature_collisions.data['dt'] = dt


    creature_plant_collisions = space.add_collision_handler(2, 6)

    creature_plant_collisions.pre_solve = process_creature_plant_collisions

    creature_plant_collisions.data['dt'] = dt

    creature_plant_collisions.data['creatures_num'] = creatures_num


    creature_meat_collisions = space.add_collision_handler(2, 10)

    creature_meat_collisions.pre_solve = process_creature_meat_collisions

    creature_meat_collisions.data['dt'] = dt

    creature_meat_collisions.data['creatures_num'] = creatures_num


    creature_rock_collisions = space.add_collision_handler(2, 8)

    creature_rock_collisions.pre_solve = process_creatures_rock_collisions

    creature_rock_collisions.data['dt'] = dt


    creature_collisions_end = space.add_collision_handler(2, 2)
    creature_collisions_end.separate = process_creatures_collisions_end


    creature_plant_collisions_end = space.add_collision_handler(2, 6)
    creature_plant_collisions_end.separate = process_creatures_plant_collisions_end


    creature_meat_collisions_end = space.add_collision_handler(2, 10)

    creature_meat_collisions_end.separate = process_creatures_meat_collisions_end


    creature_spike_collision = space.add_collision_handler(2, 32)

    creature_spike_collision.pre_solve = process_creature_spike_collision

    #creature_spike_collision.data['dt'] = dt


    meat_rock_collisions = space.add_collision_handler(10, 8)

    meat_rock_collisions.pre_solve = process_meat_rock_collisions

    meat_rock_collisions.data['dt'] = dt


    meat_rock_collisions_end = space.add_collision_handler(10, 8)

    meat_rock_collisions_end.separate = process_meat_rock_collisions_end


    plant_rock_collisions = space.add_collision_handler(6, 8)

    plant_rock_collisions.pre_solve = process_plant_rock_collisions

    plant_rock_collisions.data['dt'] = dt


    plant_rock_collisions_end = space.add_collision_handler(6, 8)

    plant_rock_collisions_end.separate = process_plant_rock_collisions_end


    spike_rock_collision = space.add_collision_handler(32, 8)

    spike_rock_collision.pre_solve = process_spike_rock_collision_begin


    rock_rock_collisions = space.add_collision_handler(8, 8)

    rock_rock_collisions.pre_solve = process_rock_rock_collisions



    #DETECTIONS:

    creature_detection = space.add_collision_handler(4, 2)

    creature_detection.pre_solve = process_agents_seeing
   

    plant_detection = space.add_collision_handler(4, 6)

    plant_detection.pre_solve = process_plants_seeing
  

    meat_detection = space.add_collision_handler(4, 10)

    meat_detection.pre_solve = process_meats_seeing


    rock_detection = space.add_collision_handler(4, 8)

    rock_detection.pre_solve = process_rocks_seeing




#^      [[[====DIRECT CONTACTS====]]]


#?  [[[ENEMYS CONTACT]]]

def process_creatures_collisions(arbiter, space, data):

    dt = data['dt']

    agent: Creature = arbiter.shapes[0].body

    target: Creature = arbiter.shapes[1].body

    if not agent.collide_time:

        return False

    dt=cfg.COLLIDE_TIME

    size0 = arbiter.shapes[0].radius

    size1 = arbiter.shapes[1].radius

    agent_tl = arbiter.normal*(size1/size0)*0.4

    target_tl = arbiter.normal*(size0/size1)*0.4

    agent.position -= agent_tl + agent_tl*agent.running

    target.position += target_tl + target_tl*target.running

    if agent.attacking and not agent.stunt:

        if abs(agent.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 60:

            if target.stunt or (agent.power + agent.size + randint(0, 10)) > (target.power + target.size + randint(0, 10)):

                dmg = cfg.HIT * ((agent.size+agent.power)/2) * dt

                target.hidding = False

                if target.hit(dmg):

                    agent.fitness += cfg.KILL2FIT

                    agent.kills += 1

                else:

                    agent.fitness += dmg*cfg.HIT2FIT

                eng = diet(agent.food, cfg.DIET_MOD) * dmg * cfg.DMG2ENG

                agent.eat(eng)

    agent.collide_creature = True

    return False


def process_creatures_collisions_end(arbiter, space, data):

    return False


def process_creature_spike_collision(arbiter, space, data):

    agent: Creature = arbiter.shapes[0].body

    spike: Spike = arbiter.shapes[1].body

    if agent == spike.owner:

        return False

    agent.stunt=True

    agent.running=False

    agent.timer["stunt"].mod_time(spike.power*(1.4-agent.size/cfg.CREATURE_MAX_SIZE))

    spike.lifetime.mod_time(-spike.lifetime.interval)

    return False


#?  [[[PLANT CONTACT]]]

def process_creature_plant_collisions(arbiter, space, data):

    dt = data['dt']

    hunter: Creature = arbiter.shapes[0].body

    target: Plant = arbiter.shapes[1].body

    if not hunter.collide_time:

        return False

    dt=cfg.COLLIDE_TIME

    size0 = arbiter.shapes[0].radius

    size1 = arbiter.shapes[1].radius

    hunter_tl: float = 0.0

    target_tl: float = 0.0


    if size0 != 0:

        hunter_tl = arbiter.normal*(size1/size0)*0.4

    else:

        hunter_tl = arbiter.normal*0.2

    hunter.position -= hunter_tl + hunter_tl*hunter.running


    if size1 != 0:

        target_tl = arbiter.normal*(size0/size1)*0.4

    else:

        target_tl = arbiter.normal*0.2

    target.position += target_tl
    

    if hunter.eating and not hunter.stunt:

        if abs(hunter.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 60:

            target.color0 = Color('yellow')

            eat = cfg.EAT * ((size0+6)/2) * dt

            target.energy = target.energy - eat

            vege = diet(11-hunter.food, cfg.DIET_MOD)

            plant_value = eat*vege*cfg.VEGE2ENG

            hunter.eat(plant_value)

            hunter.fitness += plant_value*cfg.VEGE2FIT/size0

    hunter.collide_plant = True

    return False


def process_creatures_plant_collisions_end(arbiter, space, data):

    return False


#?  [[[MEAT CONTACT]]]

def process_creature_meat_collisions(arbiter, space, data):

    dt = data['dt']

    hunter = arbiter.shapes[0].body

    target = arbiter.shapes[1].body

    if not hunter.collide_time:

        return False

    dt=cfg.COLLIDE_TIME

    size0 = arbiter.shapes[0].radius

    size1 = arbiter.shapes[1].radius

    if size0 != 0:

        hunter.position -= arbiter.normal*(size1/size0)*0.4

    else:

        hunter.position -= arbiter.normal*0.2

    size1 = arbiter.shapes[1].radius

    if size1 != 0:

        target.position += arbiter.normal*(size0/size1)*0.4

    else:

        target.position += arbiter.normal*0.2

    if hunter.eating and not hunter.stunt:

        if abs(hunter.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 60:

            target.color0 = Color('yellow')

            eat = cfg.EAT * ((size0+6)/2) * dt

            target.energy = target.energy - eat

            meat = diet(hunter.food, cfg.DIET_MOD)

            meat_value = eat * meat * cfg.MEAT2ENG

            hunter.eat(meat_value)

            hunter.fitness += meat_value*cfg.MEAT2FIT/size0

    hunter.collide_meat = True

    return False


def process_creatures_meat_collisions_end(arbiter, space, data):

    return False


#?  [[[ROCK CONTACT]]]

def process_creatures_rock_collisions(arbiter, space, data):

    agent: Creature=arbiter.shapes[0].body

    if not agent.collide_time:

        return False

    dt=cfg.COLLIDE_TIME

    arbiter.shapes[0].body.position -= arbiter.normal * 1.5

    arbiter.shapes[0].body.collide_something = True

    arbiter.shapes[0].body.border = True

    return False


def process_creatures_rock_collisions_end(arbiter, space, data):

    arbiter.shapes[0].body.collide_something = False

    return False


#?  [[[ROCK-MEAT CONTACT]]]

def process_meat_rock_collisions(arbiter, space, data):

    arbiter.shapes[0].body.position -= arbiter.normal

    return False


def process_meat_rock_collisions_end(arbiter, space, data):

    return False


#?  [[[ROCK-PLANT CONTACT]]]

def process_plant_rock_collisions(arbiter, space, data):

    plant: Plant =  arbiter.shapes[0].body

    if not plant.repro_time:

        return False

    dt=cfg.COLLIDE_TIME*5

    plant.position -= arbiter.normal*dt

    return False


def process_plant_rock_collisions_end(arbiter, space, data):

    return False


def process_spike_rock_collision_begin(arbiter, space, data):

    spike: Spike = arbiter.shapes[0].body

    spike.free()

    return False


#?  [[[ROCK-ROCK CONTACT]]]

def process_rock_rock_collisions(arbiter, space, data):

    rock1: Rock = arbiter.shapes[0].body

    rock2: Rock = arbiter.shapes[1].body

    rock2.collide_rock=True

    return False



#^      [[[====SEEING DETECTION====]]]


#?  [[[SEEING ENEMY]]]

def process_agents_seeing(arbiter: Arbiter, space: Space, data):

    agent1: Creature = arbiter.shapes[0].body

    if not agent1.vision.observe:

        return False

    agent2: Creature = arbiter.shapes[1].body

    if agent2.hidding:

        return False

    dist = agent2.position.get_dist_sqrd(agent1.position)

    if dist > agent1.vision.max_dist_enemy:

        return False

    close_object: bool=False

    filter: ShapeFilter=ShapeFilter()

    if not line_of_sight(space, agent1.ahead, agent2.position, filter):

        return False

    if pow((agent1.size*3+cfg.CLOSE_VISION), 2) >= dist:

        close_object = True

    v = agent2.position - agent1.position

    f = agent1.rotation_vector

    n = v.normalized()

    angle = f.get_angle_between(n)

    agent1.vision.add_detection(angle=angle, dist=int(dist), target=agent2, type='creature', close_object=close_object)

    return False


def process_agents_seeing_end(arbiter, space, data):

    return False



#?  [[[SEEING PLANT]]

def process_plants_seeing(arbiter: Arbiter, space: Space, data):

    agent1: Creature = arbiter.shapes[0].body

    if not agent1.vision.observe:

        return False

    agent2 = arbiter.shapes[1].body

    dist = agent2.position.get_dist_sqrd(agent1.position)

    if dist > agent1.vision.max_dist_plant:

        return False

    close_object: bool=False

    filter: ShapeFilter=ShapeFilter()

    if not line_of_sight(space, agent1.ahead, agent2.position, filter):

        return False

    if pow((agent1.size*3+cfg.CLOSE_VISION), 2) >= dist:

        close_object = True

    v = agent2.position - agent1.position

    f = agent1.rotation_vector

    n = v.normalized()

    angle = f.get_angle_between(n)

    agent1.vision.add_detection(angle=angle, dist=int(dist), target=agent2, type='plant', close_object=close_object)

    return False


def process_plants_seeing_end(arbiter, space, data):

    return False



#?  [[[SEEING MEAT]]]

def process_meats_seeing(arbiter: Arbiter, space: Space, data):

    agent1: Creature = arbiter.shapes[0].body

    if not agent1.vision.observe:

        return False

    agent2 = arbiter.shapes[1].body

    dist = agent2.position.get_dist_sqrd(agent1.position)

    if dist > agent1.vision.max_dist_meat:

        return False

    close_object: bool=False

    filter: ShapeFilter=ShapeFilter()

    if not line_of_sight(space, agent1.ahead, agent2.position, filter):

        return False

    if pow((agent1.size*3+cfg.CLOSE_VISION), 2) >= dist:

        close_object = True

    v = agent2.position - agent1.position

    f = agent1.rotation_vector

    n = v.normalized()

    angle = f.get_angle_between(n)

    agent1.vision.add_detection(angle=angle, dist=int(dist), target=agent2, type='meat', close_object=close_object)

    return False


def process_meats_seeing_end(arbiter, space, data):

    return False



def process_rocks_seeing(arbiter: Arbiter, space, data):

    agent1 = arbiter.shapes[0].body

    if not agent1.vision.observe:

        return False

    rock = arbiter.shapes[1].body
    collisions = arbiter.contact_point_set

    rock_pos: Vec2d=None

    for col_point in collisions.points:

        if not rock_pos:

            rock_pos = col_point.point_b

        else:

            rock_pos += col_point.point_b

    if len(collisions.points) > 1:

        rock_pos = rock_pos/(len(collisions.points))

    dist = rock_pos.get_dist_sqrd(agent1.position)

    if dist > agent1.vision.max_dist_rock:

        return False

    v = rock_pos - agent1.position

    f = agent1.rotation_vector

    n = v.normalized()

    angle = f.get_angle_between(n)

    tg: Target=Target(TARGET_TYPE.ROCK, rock_pos, dist, angle)

    agent1.vision.add_detection(angle=angle, dist=int(dist), target=tg, type='rock', close_object=False)

    return False