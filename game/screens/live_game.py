import pygame
import sys
from game_manager import GameManager

def start_live_game():
    while True:
        GameManager.draw_static_background()
        GameManager.draw_car()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.socket_man.socket.close()
                pygame.quit()
                sys.exit()

        pygame.display.update()    