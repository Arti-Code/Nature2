from random import random, randint
import pymunk
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
import pygame
from pygame import Color
from lib.config import *

def process_creature_plant_collisions(arbiter, space, data):
    dt = data['dt']
    hunter = arbiter.shapes[0].body
    target = arbiter.shapes[1].body
    size0 = arbiter.shapes[0].radius
    size1 = arbiter.shapes[1].radius
    if size0 != 0:
        hunter.position -= arbiter.normal*size1/size0*0.2
    else:
        hunter.position -= arbiter.normal*0.2
    size1 = arbiter.shapes[1].radius
    if size1 != 0:
        target.position += arbiter.normal*size0/size1*0.2
    else:
        target.position += arbiter.normal*0.2
    if hunter.output[3] >= 0.2:
        if abs(hunter.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 45:
            target.color0 = Color('yellow')
            target.energy = target.energy - cfg.EAT*dt
            vege = 11-hunter.food/10
            #vege = hunter.vege/((hunter.vege+hunter.meat)/2)
            plant_value = cfg.EAT*dt*vege/10*cfg.VEGE2ENG
            hunter.eat(plant_value)
            hunter.fitness += plant_value*cfg.VEGE2FIT
    hunter.collide_plant = True
    return True

def process_creature_meat_collisions(arbiter, space, data):
    dt = data['dt']
    hunter = arbiter.shapes[0].body
    target = arbiter.shapes[1].body
    size0 = arbiter.shapes[0].radius
    size1 = arbiter.shapes[1].radius
    #~ new changes
    if size0 != 0:
        hunter.position -= arbiter.normal*size1/size0*0.2
    else:
        hunter.position -= arbiter.normal*0.2
    size1 = arbiter.shapes[1].radius
    if size1 != 0:
        target.position += arbiter.normal*size0/size1*0.2
    else:
        target.position += arbiter.normal*0.2
    if hunter.output[3] >= 0.2:
        if abs(hunter.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 45:
            target.color0 = Color('yellow')
            target.energy = target.energy - cfg.EAT*dt
            meat = hunter.food/10
            meat_value = cfg.EAT*dt*(target.time/cfg.MEAT_TIME)*meat/10*cfg.MEAT2ENG
            hunter.eat(meat_value)
            hunter.fitness += meat_value*cfg.MEAT2FIT
    hunter.collide_meat = True
    return True

def process_creatures_collisions(arbiter, space, data):
    dt = data['dt']
    agent = arbiter.shapes[0].body
    target = arbiter.shapes[1].body
    size0 = arbiter.shapes[0].radius
    size1 = arbiter.shapes[1].radius
    agent.position -= arbiter.normal*size1/size0*0.5
    target.position += arbiter.normal*size0/size1*0.5
    if agent.output[4] >= 0.5:
        if abs(agent.rotation_vector.get_angle_degrees_between(arbiter.normal)) < 45:
            if (size0+randint(0, 6)) > (size1+randint(0, 6)):
                dmg = cfg.HIT * dt * (agent.size+agent.power)/2
                target.energy -= dmg
                target.color0=Color('red')
                agent.fitness += dmg*cfg.HIT2FIT
    agent.collide_creature = True
    return True

def process_edge_collisions(arbiter, space, data):
    arbiter.shapes[0].body.position -= arbiter.normal * 1.5
    arbiter.shapes[0].body.collide_something = True
    return True

def detect_creature(arbiter, space, data):
    creature = arbiter.shapes[0].body
    enemy = arbiter.shapes[1].body
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color('orange'))
            pos0 = creature.position
            dist = pos0.get_distance(enemy.position)
            sensor.send_data(detect=True, distance=dist)
            break
    return True

def detect_plant(arbiter, space, data):
    creature = arbiter.shapes[0].body
    plant = arbiter.shapes[1].body
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color('green'))
            pos0 = creature.position
            dist = pos0.get_distance(plant.position)
            sensor.send_data2(detect=True, distance=dist)
            break
    return True

def detect_obstacle(arbiter, space, data):
    creature = arbiter.shapes[0].body
    obstacle = arbiter.shapes[1].body
    contact = arbiter.contact_point_set.points[0].point_a
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color('skyblue'))
            pos0 = creature.position
            dist = pos0.get_distance(contact)
            sensor.send_data3(detect=True, distance=dist)
            break
    return True

def detect_meat(arbiter, space, data):
    creature = arbiter.shapes[0].body
    meat = arbiter.shapes[1].body
    contact = arbiter.contact_point_set.points[0].point_a
    sensor_shape = arbiter.shapes[0]
    for sensor in creature.sensors:
        if sensor.shape == sensor_shape:
            sensor.set_color(Color('red'))
            pos0 = creature.position
            dist = pos0.get_distance(contact)
            sensor.send_data4(detect=True, distance=dist)
            break
    return True

def detect_plant_end(arbiter, space, data):
    return True

def detect_creature_end(arbiter, space, data):
    return True

def detect_obstacle_end(arbiter, space, data):
    return True

def detect_meat_end(arbiter, space, data):
    return True