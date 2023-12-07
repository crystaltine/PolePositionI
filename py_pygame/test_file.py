import pygame
import sys
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
FPS = pygame.time.Clock()
#player = User(Sprite) insert sprite later

#call object instances outside the loop
while running:
    FPS.tick(24) #moved timer into loop
    screen.blit(grass, (0, 400))
    screen.blit(mtns, (0, 200))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
   
   
    #white screen works, apparently screen.fill(white) is only step 1, update() below or the flip() implements changes onto display
    pygame.display.update()

    #key numbers for keydowbs binary onkeyevent -> send to server
    #up: 00
    #down: 01
    #left: 10
    #right: 11

    #keydown: 1##
    #keyup: 0##

   
pygame.quit
sys.exit()
