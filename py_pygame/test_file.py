import pygame, sys
from pygame.locals import*
from user import User
from enemy import Enemy


pygame.init()
clock = pygame.time.Clock()
running = True
	
WHITE = (255, 255, 255)

DISPLAYSURF = pygame.display.set_mode((300,300))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

FPS = pygame.time.Clock()
FPS.tick(24)
#player = User(Sprite) insert sprite later

while running:
    for event in pygame.event.get():              
        if event.type == QUIT:
            running = false
    DISPLAYSURF.fill()
    #player.update()

    
pygame.quit
sys.exit()