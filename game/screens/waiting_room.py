import pygame
import sys

from game_manager import GameManager
from CONSTANTS import BUTTON_MEDIUM
from elements.button import Button

def waiting_room():
    """
    Creates/Mounts the room where the user is sent after creating/joining a room
    """
    
    side_panel = pygame.surface.Surface((320,720), masks=(190, 136, 59))
    start_button = Button((920,620), "START GAME", "#ffffff", "#96faff", BUTTON_MEDIUM)
    
    while True:
        GameManager.draw_static_background()
        
        GameManager.screen.blit(side_panel, (880,0))    
        
        start_button.changeColor(pygame.mouse.get_pos())
        start_button.update(GameManager.screen)    
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  
        
        pygame.display.update()   