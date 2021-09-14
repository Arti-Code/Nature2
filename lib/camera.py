from pygame.math import Vector2
from pygame import Rect


class Camera():

    def __init__(self, center: Vector2, size: Vector2):
        self.center = center
        self.size = size
        self.rect: Rect=None
        self.update()

    def update(self, move: Vector2=Vector2(0, 0)):
        self.center += move
        self.rect = Rect(int(self.center.x-self.size.x/2), int(self.center.y-self.size.y/2), self.size.x, self.size.y)

    def rel_pos(self, position: Vector2) -> Vector2:
        rx = position.x - self.rect.left
        ry = position.y - self.rect.top
        return Vector2(rx, ry)

    def rev_pos(self, position: Vector2) -> Vector2:
        rx = position.x + self.rect.left
        ry = position.y + self.rect.top
        return Vector2(rx, ry)

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