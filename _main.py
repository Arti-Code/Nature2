import sys
from random import random, randint
import pygame
import pygame.gfxdraw as gfx
from pygame import Surface, Color, Rect
import pymunk as pm
from pymunk import Vec2d, Space, Segment, Body, Circle


def draw_collision(arbiter, space, data):
    for c in arbiter.contact_point_set.points:
        r = max(3, abs(c.distance * 5))
        r = int(r)
        p = tuple(map(int, c.point_a))
        pygame.draw.circle(data["surface"], Color("red"), p, r, 0)

def add_life():
    mass = randint(1, 6)
    radius = mass + 1
    inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
    body = Body(mass, inertia)
    x = randint(100, 800)
    y = randint(100, 500)
    body.position = x, y
    impulse = Vec2d(randint(-200, 200), randint(-200, 200))
    body.apply_impulse_at_local_point(impulse)
    shape = Circle(body, radius, (0, 0))
    shape.elasticity = 0.99
    return (body, shape)

def add_wall(body: Body, point0: tuple, point1: tuple, thickness: float) -> Segment:
    segment = Segment(body, point0, point1, thickness)
    segment.elasticity = 0.99
    return segment

def main(world_size: tuple=(900, 600), view_size: tuple=(900, 600)):
    pygame.init()
    screen = pygame.display.set_mode(view_size)
    clock = pygame.time.Clock()
    running = True

    space = Space()
    space.gravity = (0.0, 0.0)
    space.damping = 1.0

    static_lines = [
        add_wall(space.static_body, (0, 0), (900, 0), 20),
        add_wall(space.static_body, (900, 0), (900, 600), 20),
        add_wall(space.static_body, (900, 600), (0, 600), 20),
        add_wall(space.static_body, (0, 600), (0, 0), 20)
    ]
    space.add(*static_lines)

    balls = []
    for i in range(50):
        body, shape = add_life()
        space.add(body, shape)
        balls.append(shape)

    ch = space.add_collision_handler(0, 0)
    ch.data["surface"] = screen
    #ch.post_solve = draw_collision

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pygame.image.save(screen, "contact_and_no_flipy.png")

        screen.fill(Color("navy"))
        balls_to_remove = []
        for ball in balls:
            if ball.body.position.y > 600 or ball.body.position.y < 0 or ball.body.position.x > 900 or ball.body.position.x < 0:
                balls_to_remove.append(ball)
            pos = ball.body.position
            gfx.filled_circle(screen, int(pos.x), int(pos.y), int(ball.radius), Color("green"))
            gfx.circle(screen, int(pos.x), int(pos.y), int(ball.radius), Color("orange"))
            gfx.circle(screen, int(pos.x), int(pos.y), int(ball.radius-1), Color("orange"))
            gfx.circle(screen, int(pos.x), int(pos.y), int(ball.radius-2), Color("orange"))
        for ball in balls_to_remove:
            space.remove(ball, ball.body)
            balls.remove(ball)
        for line in static_lines:
            body = line.body
            p1 = tuple(map(int, body.position + line.a.rotated(body.angle)))
            p2 = tuple(map(int, body.position + line.b.rotated(body.angle)))
            pygame.draw.lines(screen, Color("lightgray"), False, [p1, p2])

        dt = 1.0 / 30.0
        for x in range(1):
            space.step(dt)
        pygame.display.flip()
        clock.tick(30)
        pygame.display.set_caption("fps: " + str(round(clock.get_fps(), 1)))


if __name__ == "__main__":
    sys.exit(main((900, 600), (900, 600)))