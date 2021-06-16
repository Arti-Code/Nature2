import pygame as pg
from pygame import Rect, Vector2, Color, Surface, gfxdraw
from lib.config import *

class Viewport():

    def __init__(self, screen: Surface, width: int, height: int):
        self.view = Rect(0, 0, width, height)
        self.screen = screen
        self.width = width
        self.height = height

    def contains(self, rect: Rect):
        if self.view.contains(rect):
            return True
        else:
            return False

    def collide_rect(self, rect: Rect):
        if self.view.colliderect(rect):
            return True
        else:
            return False

    def move(self, delta: Vector2):
        self.view = self.view.move(delta.x, delta.y)

    def draw_borders(self):
        #top border
        gfxdraw.line(self.screen, self.rel_x(2), self.rel_y(2), self.rel_x(cfg['WORLDX']), self.rel_y(2), Color('red'))
        #bottom border
        gfxdraw.line(self.screen, self.rel_x(2), self.rel_y(cfg['WORLDY']), self.rel_x(cfg['WORLDX']), self.rel_y(cfg['WORLDY']), Color('red'))
        #left border
        gfxdraw.line(self.screen, self.rel_x(2), self.rel_y(2), self.rel_x(2), self.rel_y(cfg['WORLDY']), Color('red'))
        #right border
        gfxdraw.line(self.screen, self.rel_x(cfg['WORLDX']), self.rel_y(2), self.rel_x(cfg['WORLDX']), self.rel_y(cfg['WORLDY']), Color('red'))

    def rel_x(self, x):
        return x - self.view.left

    def rel_y(self, y):
        return y - self.view.top