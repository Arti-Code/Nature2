import pygame,sys
from pygame.locals import *
from lib.terrain import Terrain

pygame.init()
screen = pygame.display.set_mode((1500,900))
pygame.display.set_caption("Test")
terrain = Terrain(5, (1500, 900))
screen.blit(terrain.get_map(), (0, 0))
while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()