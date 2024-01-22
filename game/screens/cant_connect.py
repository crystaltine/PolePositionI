import time
import sys
from math import floor
from game_manager import GameManager
from CONSTANTS import *

from elements.button import Button

def cant_connect():
    """
    Used when server is not up or we can't connect.
      
    Renders a screen with a message saying that the server is not up
    """
    
    try_again_start_timestamp = time.time()
    try_again_elapsed = 0
    try_again_needed_time = 5 # seconds, go to 10, then 15, then 20, etc.
    
    while True:
        
        GameManager.TitleScreen()
        try_again_elapsed = time.time() - try_again_start_timestamp
        
        # time to try again
        if try_again_elapsed >= try_again_needed_time:
            try:
                print("Attempting to connect to server...")
                GameManager.socket_man.connect()
                return
            except ConnectionRefusedError:
                try_again_start_timestamp = time.time()
                try_again_needed_time = min(30, try_again_needed_time + 5)
                continue
        
        text = FONT_LARGE.render(
            f"Unable to connect to server. Trying again in {floor(try_again_needed_time - try_again_elapsed)} seconds...", True, BLACK
        )        
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Add the connecting... text
        GameManager.screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2 + 100))
        
        # The quit button is in a different spot specifically on this screen (since its the only button)
        QUIT_BUTTON_2 = Button(pos=(480,510), display_text="QUIT", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)
        QUIT_BUTTON_2.changeColor(mouse_pos)
        QUIT_BUTTON_2.update(GameManager.screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if QUIT_BUTTON_2.is_hovering(mouse_pos):
                    pygame.quit()
                    sys.exit()
                
        pygame.display.update()
