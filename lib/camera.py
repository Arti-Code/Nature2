from pygame.math import Vector2
from pygame import Rect
from typing import Union
from lib.math2 import clamp


class Camera():

    def __init__(self, center: Vector2, size: Vector2):
        self.center = center
        self.size = size
        self.rect: Rect=None
        self.scale_index = 3
        self.scales = [0.4, 0.6, 0.8, 1, 2, 4, 6]
        self.scale = self.scales[self.scale_index]
        self.update()

    def update(self, move: Vector2=Vector2(0, 0)):
        self.center += move
        self.rect = Rect(int(self.center.x-(self.size.x/2)*self.scale), int(self.center.y-(self.size.y/2)*self.scale), int(self.size.x*self.scale), int(self.size.y*self.scale))

    def get_offset_vec(self) -> Vector2:
        return Vector2(self.rect.x, self.rect.y)

    def get_offset_tuple(self) -> tuple:
        return (self.rect.x, self.rect.y)

    def rel_pos(self, position: Vector2) -> Vector2:
        rx = (position.x - self.rect.left)/self.scale
        ry = (position.y - self.rect.top)/self.scale
        return Vector2(int(rx), int(ry))

    def rev_pos(self, position: Vector2) -> Vector2:
        rx = (position.x + self.rect.left)/self.scale
        ry = (position.y + self.rect.top)/self.scale
        return Vector2(int(rx), int(ry))

    def point_on_screen(self, position: Vector2) -> bool:
        if self.rect.collidepoint(position.x, position.y):
            return True
        else:
            return False

    def rect_on_screen(self, rectangle: Rect) -> bool:
        if self.rect.colliderect(rectangle):
            return True
        else:
            return False

    def zoom_in(self):
        self.scale_index += 1
        self.scale_index = clamp(self.scale_index, 0, len(self.scales)-1)
        self.scale = self.scales[self.scale_index]
        self.update()

    def zoom_out(self):
        self.scale_index -= 1
        self.scale_index = clamp(self.scale_index, 0, len(self.scales)-1)
        self.scale = self.scales[self.scale_index]
        self.update()

    def zoom(self, zoom: float):
        self.scale *= zoom
        self.update()

    def reset_zoom(self):
        self.scale = 1
        self.update()