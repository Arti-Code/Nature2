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
    hunter.position -= arbiter.normal*0.5
    target.position += arbiter.normal*0.2
    target.color0 = Color('red')
    target.energy = target.energy - EAT*dt
    if target.energy > 0:
        hunter.eat(EAT*dt)
    hunter.collide_plant = True
    return True

def process_creatures_collisions(arbiter, space, data):
    dt = data['dt']
    agent = arbiter.shapes[0].body
    target = arbiter.shapes[1].body
    agent.position -= arbiter.normal*0.5
    target.position += arbiter.normal*0.5
    size0 = arbiter.shapes[0].radius
    size1 = arbiter.shapes[1].radius
    PA = target.position - agent.position
    PA = PA.normalized()
    #target_position = target.position
    #angle_to = agent.rotation_vector(target.position-agent.position)
    if (size0+randint(0, 6)) > (size1+randint(0, 6)):
        dmg = HIT * dt
        target.energy -= dmg
        target.color0=Color('red')
        agent.eat(dmg*0.85)
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
            sensor.set_color(Color('red'))
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

def detect_plant_end(arbiter, space, data):
    return True

def detect_creature_end(arbiter, space, data):
    return True

def detect_obstacle_end(arbiter, space, data):
    return True