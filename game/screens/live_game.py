import pygame
import sys
from typing import Callable, Any

from game_manager import GameManager
from renderer import GameRenderer

def live_game():
    """
    Mounts and handles tasks related to a live game on the screen. 
    
    ### IMPORTANT:
    By the time this function is called, socket should have already started listening
    because `waiting_room` should've started the recv loop.
    
    Thus, we should be receiving packets in the background here, which should be updating the world state.
    We don't really have to do anything except keep our render loop going.
    
    ^ see `SocketManager.on_packet` in `../requests_handler.py`
    """
    
    while True:
        GameRenderer.tick_world()
        GameRenderer.render_frame()
        
        for event in pygame.event.get():
            if event == pygame.QUIT:
                GameManager.quit_game()
                
            GameManager.socket_man.handle_game_keypresses(event)
        
        pygame.display.update()