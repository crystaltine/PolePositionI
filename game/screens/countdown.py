import pygame
import sys
import time
from game_manager import GameManager


def countdown():
    while True:
        GameManager.draw_static_background()
        GameManager.loop_countdown_button()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.socket_man.socket.close()
                pygame.quit()
                sys.exit()
        pygame.display.update()
        #TODO - This freezes the entire game
        time.sleep(3)
        return