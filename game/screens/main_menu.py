import pygame
import sys
from typing import Callable, Any
from time import sleep

from tkinter import *
from tkinter import messagebox, simpledialog

from game_manager import GameManager
from requests_handler import HTTPManager
from screens.waiting_room import waiting_room

# TODO generally, these tkinter popups are ugly and maybe we could replace them with in-game popups?

def onclick_multiplayer_button(callback: Callable[[bool], Any]) -> dict:
    """
    when the user clicks on a multiplayer button, 
    we need to open connections to the server.
    
    Registers the socket and http managers. 
    
    ## Btw, registering the socket is a BLOCKING CALL (stops the program (thread) until it connects)
    
    If they already exists, then do nothing.
    
    For the callback: should be a function that takes in a boolean,
    which is true if a new connection was established, false if nothing happened (httpman already exists)
    
    Returns the following dict:
    ```typescript
    {
        type: 'username-cancel', 'conn-error', 'cb-result', // username-cancel means the username popup was canceled, conn-error means the connection failed, cb-result means the callback was run (probably this function succeeded)
        callback_result?: any, // result of the callback, if user didnt cancel and connection succeeded/didnt need to be made again
    }
    ```
    result of the callback, and 'username-canceled' if the user canceled the username popup (keep looping main_menu)
    """
    
    if GameManager.http_man is None:
        # inline connects both the socket and http managers
        
        # ask for a username using a popup
        Tk().wm_withdraw() #to hide the main window
        username = simpledialog.askstring(title="Username", prompt="Please enter a username")
        
        if username is None: return { "type": "username-cancel", } # they canceled the popup
        
        # check for username validity: must have 1 < length < 12, and only contain alphanumeric characters
        while not username or len(username) < 1 or len(username) > 12 or not username.isalnum():
            Tk().wm_withdraw() #to hide the main window
            messagebox.showinfo('Invalid Username', 'Please enter a valid username (1-12 characters, alphanumeric only)')     
            
            username = simpledialog.askstring(title="Username", prompt="Please enter a username")   
            if username is None: return { "type": "username-cancel", }
        
        client_id = GameManager.socket_man.connect(username)
        
        if not client_id:
            # Connection failed. Show a popup that says "cant connect to server"
            # see https://stackoverflow.com/questions/41639671/pop-up-message-box-in-pygame
            Tk().wm_withdraw() #to hide the main window
            messagebox.showinfo('Connection Error', 'Could not connect to server. Please try again later.')
            return { "type": "conn-error", }
        
        GameManager.http_man = HTTPManager(client_id)
        
    return {
        "type": "cb-result",
        "callback_result": callback(not (GameManager.http_man is None))
    }

def main_menu() -> bool:
    """
    Creates and mounts the main menu on screen.
    
    Since this function is the entry point for the waiting room, it also returns 
    a boolean that marks the next screen to go to. 
    This value is `True` if we should proceed to live game screen (game started).
    and `False` if user left/got kicked/room disbanded, etc - in this case, we should rerun main_menu.
    """

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        GameManager.TitleScreen()
        GameManager.loop_titlescreen_buttons()
        
        for event in pygame.event.get():
            
            # for typing in the input box
            GameManager.join_game_input.handle_event(event)
            
            if event.type == pygame.QUIT:
                GameManager.socket_man.socket.close()
                pygame.quit()
                sys.exit()
                
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # LEFT CLICKS ONLY!!!
                if GameManager.create_game_button.is_hovering(mouse_pos):
                    
                    GameManager.create_game_button.display_text = "Connecting..."
                    GameManager.create_game_button.update_text(GameManager.screen)
                    pygame.display.update()
                    
                    # This is a callback for the onclick_multiplayer_button function
                    # since connecting takes noticeable time, we need to wait for it to finish
                    def _cb(new_conn):
                        res = GameManager.http_man.create_room()
                    
                        if not res.get('success'):
                            print("Error creating room!!!", res.get('message'))
                            Tk().wm_withdraw() #to hide the main window
                            messagebox.showinfo('Error', res.get('message'))
                            return None
                        
                        else:
                            print("Room created successfully! Code:", res.get('code'))
                            GameManager.room_id = res.get('code')

                            # server will return ourselves (since it assigns us a random color)
                            return waiting_room(res.get('map_data'), True, [res.get('player_data')])
                    
                    click_result = onclick_multiplayer_button(_cb)
                    # revert back to original text
                    GameManager.create_game_button.display_text = "CREATE GAME"
                    GameManager.create_game_button.update_text(GameManager.screen)
                    
                    # it is None if the user canceled the username popup/error occurred
                    # ^ in that case, we dont actually want to exit the main menu.
                    if click_result['type'] == "username-cancel" or click_result['type'] == "conn-error":
                        continue
                    
                    # returned None means an error or something. Stay on main menu
                    if click_result["callback_result"] is not None:
                        return click_result["callback_result"]
                    
                elif GameManager.join_game_button.is_hovering(mouse_pos):
                    
                    GameManager.join_game_button.display_text = "Connecting..."
                    GameManager.join_game_button.update_text(GameManager.screen)
                    pygame.display.update()

                    # This is a callback for the onclick_multiplayer_button function
                    # since connecting takes noticeable time, we need to wait for it to finish
                    def _cb(new_conn):
                        res = GameManager.http_man.join_room(GameManager.join_game_input.text)
                        
                        if not res['success']:
                            print("Error joining room!!!", res.get('message'))
                            Tk().wm_withdraw()
                            messagebox.showinfo('Error', res.get('message'))
                            return None
                        
                        else:
                            print("Room joined successfully! Code:", res.get('code'))
                            GameManager.room_id = res.get('code')
                            
                            return waiting_room(res.get('map_data'), False, res.get('players'))
                    
                    # This returns to the caller of main_menu whether or not to rerun it, or proceed.                    
                    click_result = onclick_multiplayer_button(_cb)
                    # revert back to original text
                    GameManager.join_game_button.display_text = "JOIN GAME"
                    GameManager.join_game_button.update_text(GameManager.screen)
                    
                    if click_result['type'] == "username-cancel" or click_result['type'] == "conn-error":
                        continue
                    
                    # returned None means an error or something. Stay on main menu
                    if click_result["callback_result"] is not None:
                        return click_result["callback_result"]
                    
                elif GameManager.livegametest_button.is_hovering(mouse_pos):
                    return True
                
                elif GameManager.quit_button.is_hovering(mouse_pos):
                    
                    # close the sockets
                    GameManager.socket_man.socket.close()
                    
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()
       