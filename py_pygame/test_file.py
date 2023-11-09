import pygame
from pygame.locals import*

pygame.init()
	
WHITE = (255, 255, 255)

DISPLAYSURF = pygame.display.set_mode((300,300))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

FPS = pygame.time.Clock()
FPS.tick(24)
