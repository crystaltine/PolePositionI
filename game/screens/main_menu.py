import pygame
import sys

from game_manager import GameManager

def main_menu(): # game screen
#call object instances outside the loop

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        GameManager.TitleScreen()
        GameManager.loop_titlescreen_buttons()
        
        for event in pygame.event.get():
            
            # for typing in the input box
            GameManager.join_game_input.handle_event(event)
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # LEFT CLICKS ONLY!!!
                if GameManager.create_game_button.is_hovering(mouse_pos):
                    res = GameManager.http_man.create_room()
                    
                    if not res['success']:
                        print("Error creating room!!!", res.get('message'))
                        # TODO - display message on screen, maybe a little text blurb under the button that says the message
                    
                    else:
                        print("Room created successfully! Code:", res.get('code'))
                        # TODO - display the waiting lobby
                    
                if GameManager.join_game_button.is_hovering(mouse_pos):
                    res = GameManager.http_man.join_room(GameManager.join_game_input.text)
                    
                    if not res['success']:
                        print("Error joining room!!!", res.get('message'))
                        # TODO - display message on screen, maybe a little text blurb under the input box that says the message
                    
                    else:
                        print("Room joined successfully! Code:", res.get('code'))
                        # TODO - display the waiting lobby
                    
                if GameManager.settings_button.is_hovering(mouse_pos):
                    pass # TODO - settings menu?
                
                if GameManager.quit_button.is_hovering(mouse_pos):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()
       