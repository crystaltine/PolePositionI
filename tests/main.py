import pygame
import sys
from key_listener import capture_keypress_loop, recv_packet
pygame.init()

running = True
   
WHITE = (255, 255, 255)

screen = pygame.display.set_mode([300,300])
screen.fill(WHITE)
pygame.display.set_caption("Game")

FPS = pygame.time.Clock()

while running:
    FPS.tick(24)

    capture_keypress_loop()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    pygame.display.update()
   
pygame.quit()
sys.exit()
