import sys
from math import pi, sin, cos
from random import randint, choice, random
import pygame
from pygame.time import Clock
from pygame import Surface, Color, Rect
from pygame import gfxdraw
import pymunk
import pymunk.pygame_util
from pymunk import Circle, Poly, Space, BB, Body
from pygame.locals import *
from enum import Enum, IntEnum

class Shape2D(IntEnum):
    CIRCLE = 0
    BOX = 1

class Object2D(Body):

    def __init__(self, screen: Surface, space: Space, shape2d: Shape2D, position: tuple, size: int, color_name: str):
        super().__init__(body_type=Body.KINEMATIC)
        self.position = position
        self.size = size
        self.shape2d = shape2d
        self.color = Color(color_name)
        self.shape = None
        self.angle = random()*2*pi
        self.impulse = randint(0, 50)
        if self.shape2d == Shape2D.CIRCLE:
            self.shape = Circle(self, size)
        space.add(self, self.shape)
        #self.apply_impulse_at_local_point(imp_vector)

    def draw(self, screen: Surface):
        x = int(self.position[0]); y = int(flipy(self.position[1])); r = int(self.size)
        gfxdraw.circle(screen, x, y, r, self.color)
        gfxdraw.aacircle(screen, x, y, r, self.color)

    def update(self, dt: float):
        vec = self.rotation_vector
        self.velocity = (vec[0]*self.impulse, vec[1]*self.impulse)
        self.update_velocity(self, (0, 0), 0.2, dt)

scr_size = (900, 600)
screen: Surface=None
space: Space=None
running: bool = True
clock: Clock = None
draw_debug: bool=True
options: None
FPS: int=30
dt: float=1/FPS
objects2D: list=[]
colors = ['white', 'yellowgreen', 'green', 'darkgreen', 'limegreen', 'skyblue', 'blue', 'cyan', 'orange', 'red', 'yellow', 'magenta']

def flipy(y):
    global scr_size
    return -y + scr_size[1]

def init():
    global screen, space, objects2D, clock, options
    pygame.init()
    pygame.display.set_caption("Test")
    screen = pygame.display.set_mode(scr_size)
    space = Space()
    space.gravity = (0, 0)
    clock = Clock()
    pymunk.pygame_util.positive_y_is_up = True
    options = pymunk.pygame_util.DrawOptions(screen)
    space.debug_draw(options)
    draw_debug: bool=False
    create(triangles=0, circles=10,  boxes=0)


def create(triangles: int, circles: int, boxes: int):
    for c in range(circles):
        pos = (randint(0, scr_size[0]-1), randint(0, scr_size[1]-1))
        size = randint(3, 10)
        color_name = choice(colors)
        circle = Object2D(screen, space, Shape2D.CIRCLE, pos, size, color_name)
        objects2D.append(circle)

def update(dt: float):
    for obj in objects2D:
        obj.update(dt)

def draw(dt: float):
    screen.fill(Color('black'))
    for obj in objects2D:
        obj.draw(screen)

def events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

def clock_step():
    pygame.display.flip()
    dt = clock.tick(FPS)/1000
    pygame.display.set_caption(f"[fps: {round(clock.get_fps())} | dT: {round(dt*1000)}ms]")

def main():
    init()
    while running:
        events()
        update(dt)
        draw(dt)
        if draw_debug:
            space.debug_draw(options)
        clock_step()


if __name__ == "__main__":
    main()