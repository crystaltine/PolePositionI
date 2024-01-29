import pygame
import sys
from typing import Callable, Any

from managers import GameManager, RenderingManager

def live_game() -> bool:
    """
    Mounts and handles tasks related to a live game on the screen. 
    
    ### IMPORTANT:
    By the time this function is called, socket should have already started listening
    because `waiting_room` should've started the recv loop.
    
    Thus, we should be receiving packets in the background here, which should be updating the world state.
    We don't really have to do anything except keep our render loop going.
    
    ^ see `SocketManager.on_packet` in `../requests_handler.py`
    
    Returns when the live game ends. However, if the game_end screen must be shown,
    this function calls that (with the received data) before returning.
    
    So after this function runs, just return to the main menu. (the game_end screen also returns when user clicks "back to main menu")
    """
    
    def _leave(_):
        GameManager.live_game_proceed_code = 1
        
    def _proceed(data):
        GameManager.live_game_proceed_code = 2
        GameManager.leaderboard_data = data
    
    # create new event handler
    GameManager.socket_man.on('leave', _leave)
    GameManager.socket_man.on('game-end', _proceed)
    
    while True:
        
        if GameManager.live_game_proceed_code != 0:
            return GameManager.live_game_proceed_code == 2 # True if 2, False if 1
        
        GameManager.game_renderer.tick_world()
        RenderingManager.render_frame()
        
        for event in pygame.event.get():
            if event == pygame.QUIT:
                GameManager.quit_game()
                
            GameManager.socket_man.handle_game_keypresses(event)
        
        pygame.display.update()