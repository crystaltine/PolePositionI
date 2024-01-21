import pygame
import sys
import random
pygame.init()

running = True
   
SKY = (97, 120, 232)

width = pygame.display.get_desktop_sizes()[0][0]
height = pygame.display.get_desktop_sizes()[0][1]

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
size = pygame.display.get_desktop_sizes()
grass = pygame.image.load('grasse.png')
grass = pygame.transform.scale(grass, (width, 2 * height/3))
mtns = pygame.image.load('mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))
road = pygame.image.load('straightRoad.gif')
road = pygame.transform.scale(road, (width, 4*height/3))
FPS = pygame.time.Clock()
#player = User(Sprite) insert sprite later

#call object instances outside the loop
while running:
    FPS.tick(24) #moved timer into loop
    screen.blit(grass, (0, 2*height/5))
    screen.blit(mtns, (0, height/5))
    screen.blit(road, (0, -height/5))
    for event in pygame.event.get():
        

        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
   
pygame.quit()
sys.exit()
