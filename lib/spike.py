from math import cos, degrees, sin, sqrt

import pygame.gfxdraw as gfxdraw
from pygame import draw
from pygame import Color, Surface
from pygame.math import Vector2
from pymunk import Body, Circle, Vec2d, Segment, Space

from lib.camera import Camera
from lib.config import cfg
from lib.math2 import clamp
from lib.utils import Timer
from lib.life import Life


class Spike(Body):

    COLOR = (255, 255, 0)
    SPEED = 100
    LIFETIME = 1.0
    SIZE = 2

    def __init__(self, space: Space, owner: Life, pos: Vec2d, pow: float, angle: float, life_time: float):
        super().__init__(self, body_type=Body.KINEMATIC)
        self.owner = owner
        self.position = pos
        self.angle = angle
        self.power = pow
        b = (Vec2d(cos(angle), sin(angle))*2)
        self.shape: Segment = Segment(self, a=-b, b=b, radius=pow)
        self.shape.collision_type = 32
        space.add(self, self.shape)
        self.lifetime:Timer = Timer(life_time, True, True, "spike", False)

    def update(self, dt: float) -> bool:
        if self.lifetime.timeout(dt):
            return False
        move = Vec2d(cos(self.angle), sin(self.angle))*self.SPEED*dt
        self.position += move
        return True

    def draw(self, screen: Surface, camera: Camera):
        if not camera.rect_on_screen(self.shape.bb):
            return
        #rel_pos = camera.rel_pos(self.position)
        a = camera.rel_pos(self.position+self.shape.a)
        b = camera.rel_pos(self.position+self.shape.b)
        draw.line(screen, self.COLOR, a, b, 2)

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)
        del self

    def free(self):
        self.lifetime.overload()