import pygame
import sys
pygame.init()

running = True
   
WHITE = (255, 255, 255)

screen = pygame.display.set_mode([300,300])
screen.fill(WHITE)
pygame.display.set_caption("Game")

FPS = pygame.time.Clock()
#player = User(Sprite) insert sprite later

#call object instances outside the loop
while running:
    FPS.tick(24) #moved timer into loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
   
   
    #white screen works, apparently screen.fill(white) is only step 1, update() below or the flip() implements changes onto display
    pygame.display.update()

   
pygame.quit
sys.exit()
