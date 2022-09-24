from enum import Enum, auto
from math import cos
from math import pi as PI
from math import sin
from random import gauss, random
from enum import IntEnum
from pygame import Color, Rect, Surface
from pygame.draw import polygon
from pygame.math import Vector2
from pymunk import Body, Poly, Space, Vec2d

from lib.camera import Camera
from lib.math2 import flipy

FILL_COLOR:     Color=Color('grey20')
BORDER_COLOR:   Color=Color('darkgray')

class LONG_AXE(IntEnum):
    X: auto()
    Y: auto()

class Rock(Body):

    def __init__(self, space: Space, vertices: int, size: int, position: Vec2d, thickness: float=1.0):
        super().__init__(body_type=Body.STATIC)
        self.border_color = BORDER_COLOR
        self.fill_color = FILL_COLOR
        self.vertices = self.create_vertices(vertices_num=vertices, size=size, position=position)
        self.shape = Poly(self, self.vertices, None, thickness)
        self.shape.collision_type = 8
        self.points = []
        self.rect = self.create_bb()
        space.add(self, self.shape)

    def create_vertices(self, vertices_num: int, size: int, position: Vec2d) -> list[Vec2d]:
        if vertices_num < 3:
            vertices_num = 3
        radian_step: float=(2*PI)/vertices_num
        alfa: float=(2*PI)*random()
        points: list[Vec2d]=[]
        for _ in range(vertices_num):
            s: float=gauss(size, size/4)
            x: int; y: int
            x = int(sin(alfa)*s)
            y = int(cos(alfa)*s)
            points.append(Vec2d(x+position[0], y+position[1]))
            alfa += radian_step
        return points

    def create_bb(self) -> Rect:
        x_axe = []
        y_axe = []
        for vert in self.shape.get_vertices():
            self.points.append((int(vert[0]), flipy(int(vert[1]))))
            x_axe.append((int(vert[0])))
            y_axe.append(flipy(int(vert[1])))
        x_min = min(x_axe)
        x_max = max(x_axe)
        y_min = min(y_axe)
        y_max = max(y_axe)
        return Rect(x_min, y_min, x_max-x_min, y_max-y_min)

    def draw(self, screen: Surface, camera: Camera) -> bool:
        if not camera.rect_on_screen(self.rect):
            return False
        #t = int(self.shape.radius)
        pts = []
        for p in self.points:
            rel_pts = camera.rel_pos(Vector2(p[0], p[1]))
            pts.append((rel_pts.x, rel_pts.y))
        polygon(screen, self.fill_color, pts, 0)
        polygon(screen, self.border_color, pts, 4)
        return True

    def update(self, dT: float):
        pass

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)


class Wall(Body):

    def __init__(self, space: Space, begin: tuple[int], end: tuple[int], width: int):
        super().__init__(body_type=Body.STATIC)
        w: int= width//2
        long_axe="x"
        xxx: int=abs(end[0]-begin[0])
        yyy: int=abs(end[1]-begin[1])
        wvec: tuple[int]
        if xxx < yyy:
            long_axe = "y"
        if long_axe == "x":
            wvec=(0, w)
        elif long_axe == "y":
            wvec=(w, 0)
        p0 = Vec2d(begin[0]-wvec[0], begin[1]-wvec[1])
        p1 = Vec2d(end[0]-wvec[0], end[1]-wvec[1])
        p2 = Vec2d(end[0]+wvec[0], end[1]+wvec[1])
        p3 = Vec2d(begin[0]+wvec[0], begin[1]+wvec[1])
        self.vertices: list[tuple]=[p0, p1, p2, p3]
        self.shape = Poly(self, self.vertices)
        self.shape.collision_type = 8
        self.points = []
        self.rect = self.create_bb()
        space.add(self, self.shape)

    def create_bb(self) -> Rect:
        x_axe = []
        y_axe = []
        for vert in self.shape.get_vertices():
            self.points.append((int(vert[0]), flipy(int(vert[1]))))
            x_axe.append((int(vert[0])))
            y_axe.append(flipy(int(vert[1])))
        x_min = min(x_axe)
        x_max = max(x_axe)
        y_min = min(y_axe)
        y_max = max(y_axe)
        return Rect(x_min, y_min, x_max-x_min, y_max-y_min)

    def draw(self, screen: Surface, camera: Camera) -> bool:
        if not camera.rect_on_screen(self.rect):
            return False
        pts = []
        for p in self.points:
            rel_pts = camera.rel_pos(Vector2(p[0], p[1]))
            pts.append((rel_pts.x, rel_pts.y))
        polygon(screen, FILL_COLOR, pts, 0)
        polygon(screen, BORDER_COLOR, pts, 4)
        return True

    def update(self, dT: float):
        pass

    def kill(self, space: Space):
        space.remove(self.shape)
        space.remove(self)