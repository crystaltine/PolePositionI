import pygame
from typing import Callable, Any

from managers import GameManager
from CONSTANTS import *

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
    
    us = GameManager.get_our_entity()
    
    def _leave(_):
        GameManager.live_game_proceed_code = 1
        
    def _proceed(data):
        GameManager.leaderboard_data = data
        GameManager.live_game_proceed_code = 2
        
    def _crash(crash_data):
        # set our new physics
        GameManager.last_y_pos = us.pos[1] # save this for the crash animation
        GameManager.crash_end_timestamp = crash_data['crash_end_timestamp']
        us.crash_end_timestamp = crash_data['crash_end_timestamp']
        us.set_physics(crash_data['new_physics'])
        crash_sound.play()
        
    # create new event handler
    GameManager.socket_man.on('leave', _leave)
    GameManager.socket_man.on('game-end', _proceed)
    GameManager.socket_man.on('crash', _crash)
    
    while True:

        if GameManager.live_game_proceed_code != 0:
            return GameManager.live_game_proceed_code == 2 # True if 2, False if 1
        
        GameManager.game_renderer.tick_world()
        GameManager.game_renderer.render_frame()
        
        for event in pygame.event.get():
            if event == pygame.QUIT:
                GameManager.quit_game()

                
            GameManager.socket_man.handle_game_keypresses(event)
        
        # Speed text
        velocity_mph = us.vel * 2.237
        speedometer_text = FONT_LARGE.render(f"{velocity_mph:.1f} mph", True, (255, 255, 255))
        GameManager.screen.blit(speedometer_text, (20, 20))
        
        # 800px, right-aligned progress bar
        pbar_frame_x, pbar_frame_y = 380, 8
        pbar_fill_x, pbar_fill_y = pbar_frame_x, 20
        
        # the texture itself is 1026px wide. pbar should be 43px tall, but frame has a bit of decoration spanning 12px at the top.
        progressbar_filled_width = us.get_progress() * 800
        pygame.draw.rect(GameManager.screen, (248, 195, 24), pygame.Rect((pbar_fill_x, pbar_fill_y), (progressbar_filled_width, 43)))
        GameManager.screen.blit(GameManager.progressbar_img, (pbar_frame_x, pbar_frame_y))
        
        pygame.display.update()