from dataclasses import dataclass
from pygame import Surface, Color, Rect
from pygame import gfxdraw as gfx
from lib.camera import Camera

@dataclass
class Field:
    x: int
    y: int
    d: int
    w: int

class Land:

    def __init__(self, size: tuple[int, int], square_size: int):
        self.size = size
        self.square = square_size
        self.fields: list[list[Field]]

    def fill_land(self, depth: int=0, water: int=0):
        w, h = self.size
        for row in range(h):
            column: list[Field]=[]
            for col in range(w):
                field: Field=Field(col, row, depth, water)
                column.append(field)
            self.fields.append(column)

    def draw(self, screen: Surface, camera: Camera):
        pass