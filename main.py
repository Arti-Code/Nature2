import sys
from random import random, randint
import pygame
import pygame.gfxdraw as gfx
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Space, Segment, Body, Circle, Shape
from lib.life import Life
from lib.wall import Wall

def draw_collision(arbiter, space, data):
    for c in arbiter.contact_point_set.points:
        r = max(3, abs(c.distance * 5))
        r = int(r)
        p = tuple(map(int, c.point_a))
        pygame.draw.circle(data["surface"], Color("red"), p, r, 0)
        print('collision')

def add_life(screen: Surface) -> tuple[Body, Shape, Life]:
    """ function with add single life to simulated world """
    size = randint(3, 10)
    life = Life(screen=screen, world_size=Vec2d(900, 600), size=size, color0=Color('green'), color1=Color('yellow'), color2=Color('skyblue'))
    body, shape = life.get_body_and_shape()
    return (body, shape, life)

def add_wall(screen: Surface, point0: tuple, point1: tuple, thickness: float) -> tuple[Body, Shape, Wall]:
    """ function with add single wall to simulated world """
    wall = Wall(screen, point0, point1, thickness, Color('gray'), Color('gray'))
    body, shape = wall.get_body_and_shape()
    return (body, shape, wall)

def main(world_size: tuple=(900, 600), view_size: tuple=(900, 600)):
    pygame.init()
    screen = pygame.display.set_mode(view_size)
    clock = pygame.time.Clock()
    running = True; dt = 330
    space = Space()
    space.gravity = (0.0, 0.0)

    life_list = []; wall_list = []

    body, shape, wall = add_wall(screen, (5, 5), (895, 5), 5)
    space.add(body, shape)
    wall_list.append(wall)

    body, shape, wall = add_wall(screen, (895, 5), (895, 595), 5)
    space.add(body, shape)
    wall_list.append(wall)

    body, shape, wall = add_wall(screen, (895, 595), (5, 595), 5)
    space.add(body, shape)
    wall_list.append(wall)
    
    body, shape, wall = add_wall(screen, (5, 595), (5, 5), 5)
    space.add(body, shape)
    wall_list.append(wall)

    for _ in range(50):
        body, shape, life = add_life(screen)
        space.add(body, shape)
        life_list.append(life)

    ch = space.add_collision_handler(0, 0)
    ch.data["surface"] = screen
    ch.post_solve = draw_collision

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pygame.image.save(screen, "contact_and_no_flipy.png")

        screen.fill(Color("black"))
        for life in life_list:
            life.update(dt)
            life.draw()

        for wall in wall_list:
            wall.draw()

        dt = 1.0 / 30.0
        for x in range(1):
            space.step(dt)
        pygame.display.flip()
        clock.tick(30)
        pygame.display.set_caption("NATURE v0.0.1      [fps: " + str(round(clock.get_fps(), 1)) + "]")


if __name__ == "__main__":
    sys.exit(main((900, 600), (900, 600)))