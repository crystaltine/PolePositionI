import pygame
import sys
from time import time

from game_manager import GameManager
from CONSTANTS import BUTTON_MEDIUM, FONT_TINY, FONT_MEDIUM, FONT_LARGE, FONT_SIZES
from elements.button import Button
from elements.waiting_lobby_player import waiting_lobby_player
from elements.waiting_room_main_panel import WaitingRoomMainPanel

def waiting_room(details: dict, is_leader = False) -> bool:
    """
    Creates/Mounts the room where the user is sent after creating/joining a room
    
    Just as a note, we are safe to use `GameManager.socket_man` and `GameManager.http_man` here because
    this function is only called AFTER both are successfully initialized and connected.
    
    Returns `True` if we should proceed into the game screen, `False` if we left, got kicked, or room disbanded (return to main menu)
    
    As of Jan. 26th, 1:34AM, `details` should have the following schema: (see `server/CONSTANTS.py`)
    ```python
    {
        "map_name": "fsdfksdj",
        "preview_file": "fsdfksdj.png",
        "length": 999,
        "wr_time": 55,
        # TODO - also need to somehow link to a representation of the map, so we can handle physics and stuff.
    }
    ``` 
    """
    
    main_panel = WaitingRoomMainPanel()

    side_panel = pygame.surface.Surface((280,720), pygame.SRCALPHA)
    side_panel.fill((0, 0, 0, 128))
    
    # Load the 240x240 map preview
    map_preview = pygame.image.load(f'./game/assets/lobby/maps/{details["preview_file"]}')
    side_panel.blit(map_preview, (20, 20))
    
    map_label = FONT_TINY.render("Map:", True, "#ffffff")
    map_text = FONT_MEDIUM.render(details['map_name'], True, "#ffffff")
    length_label = FONT_TINY.render("Track length:", True, "#ffffff")
    length_text = FONT_MEDIUM.render(f"{details['length']} m", True, "#ffffff")
    record_label = FONT_TINY.render("WR time:", True, "#ffffff")
    record_text = FONT_MEDIUM.render(f"{details['wr_time']} s", True, "#ffffff")
    # TODO - save pb times on client side (in a file), then fetch
    #pb_label = FONT_TINY.render("PB time:", True, "#ffffff")
    #pb_text = FONT_MEDIUM.render(f"{details['pb_time']} s", True, "#ffffff")
    
    LABEL_GAP = 5
    DESC_GAP = 20
    
    side_panel.blit(map_label, (20, 280))
    side_panel.blit(map_text, (20, 280 + FONT_SIZES["tiny"] + LABEL_GAP)) # gap of 5px between label and value
    
    side_panel.blit(length_label, (20, 280 + FONT_SIZES["tiny"] + LABEL_GAP + FONT_SIZES["medium"] + DESC_GAP)) # gap of 10px between text objects
    side_panel.blit(length_text, (20, 280 + 2*FONT_SIZES["tiny"] + 2*LABEL_GAP + FONT_SIZES["medium"] + DESC_GAP))
    
    side_panel.blit(record_label, (20, 280 + 2*FONT_SIZES["tiny"] + 2*LABEL_GAP + 2*FONT_SIZES["medium"] + 2*DESC_GAP))
    side_panel.blit(record_text, (20, 280 + 3*FONT_SIZES["tiny"] + 3*LABEL_GAP + 2*FONT_SIZES["medium"] + 2*DESC_GAP))
    
    #side_panel.blit(pb_label, (20, 280 + 3*FONT_SIZES["tiny"] + 3*LABEL_GAP + 3*FONT_SIZES["medium"] + 3*DESC_GAP))
    #side_panel.blit(pb_text, (20, 280 + 4*FONT_SIZES["tiny"] + 4*LABEL_GAP + 3*FONT_SIZES["medium"] + 3*DESC_GAP))
    
    # There is a 20px "padding" in side_panel because these buttons are 240px but the panel is 280px
    start_button = Button((940,640), "START GAME", "#ffffff", "#96faff", BUTTON_MEDIUM, disabled=(not is_leader))
    leave_button = Button((940,560), "LEAVE", "#ffffff", "#ff9696", BUTTON_MEDIUM)
    
    #####################################
    # Register player leave/join events #
    #####################################
    GameManager.socket_man.on('player-join', lambda data: main_panel.add_player(data['username'], data['color']))
    GameManager.socket_man.on('player-leave', lambda data: main_panel.remove_player(data['username']))
    
    def _start(_): 
        print(f">>> Game started event received!!!!")
        GameManager.waiting_room_game_started = True # TODO - vscode shows these as not accessed. Could it be because they are in a nested function?
    def _leave(_):
        print(f">>> Room closed event received!!!!")
        GameManager.waiting_room_leave_game = True
        
    # these actually run on a different thread, so this might work??
    GameManager.socket_man.on('game-start', _start)
    GameManager.socket_man.on('leave', _leave) # kicked, manually left, disbanded, etc.
    
    while True:
        
        if GameManager.waiting_room_game_started:
            GameManager.waiting_room_game_started = False
            return True
        if GameManager.waiting_room_leave_game:
            GameManager.waiting_room_leave_game = False
            return False
        
        GameManager.draw_static_background()
    
        text = FONT_LARGE.render(f"Waiting for start...", True, "#ffffff")
        GameManager.screen.blit(text, (20,20))
        
        GameManager.screen.blit(side_panel, (920,0))   
        GameManager.screen.blit(main_panel.generate_component(), (0,0)) 
        
        GameManager.draw_logo(720, 20, 0.25) # should be at the top right corner of the main_panel
        
        start_button.changeColor(pygame.mouse.get_pos())
        start_button.update(GameManager.screen)    
        
        leave_button.changeColor(pygame.mouse.get_pos())
        leave_button.update(GameManager.screen)
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                GameManager.socket_man.socket.close()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # left click
                if start_button.is_hovering(pygame.mouse.get_pos()):
                    # start button won't be hovering ever if it is disabled
                    # so we don't need to check if it is disabled again here.
                    # plus, server rejects all unauthorized start requests
                    GameManager.socket_man.send_event('start_game')
                elif leave_button.is_hovering(pygame.mouse.get_pos()):
                    GameManager.socket_man.send_event('leave_room')
                    return False
        
        pygame.display.update()   