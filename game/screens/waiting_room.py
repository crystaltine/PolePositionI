import pygame
import sys

from game_manager import GameManager
from CONSTANTS import BUTTON_MEDIUM
from elements.button import Button
from elements.waiting_lobby_player import waiting_lobby_player

def waiting_room():
    """
    Creates/Mounts the room where the user is sent after creating/joining a room
    """
    
    main_panel = pygame.surface.Surface((880, 720), pygame.SRCALPHA)
    main_panel.fill((255,255,255,0))
    
    # TEST - add a test player
    main_panel.blit(waiting_lobby_player("xXgamerXx", "red"), (100, 100))
    
    side_panel = pygame.surface.Surface((320,720), pygame.SRCALPHA)
    side_panel.fill((0, 0, 0,128))
    
    start_button = Button((920,620), "START GAME", "#ffffff", "#96faff", BUTTON_MEDIUM)
    
    while True:
        GameManager.draw_static_background()
        
        GameManager.screen.blit(side_panel, (880,0))   
        GameManager.screen.blit(main_panel, (0,0)) 
        
        start_button.changeColor(pygame.mouse.get_pos())
        start_button.update(GameManager.screen)    
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  
        
        pygame.display.update()   