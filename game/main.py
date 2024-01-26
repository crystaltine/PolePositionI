from game_manager import GameManager
from screens.cant_connect import cant_connect
from screens.main_menu import main_menu
from screens.waiting_room import waiting_room
from requests_handler import HTTPManager

def start_program():
    """
    This should be run on app start. Creates connections, decides which screen to send the user to
    (Main menu or connecting... screen)
    """

    ################## vvv TESTS vvv ##################
    """ THIS TESTING CODE IS CURRENTLY DISABLED (it's all commented out)
    
    # this should be obtained from server upon joining a room
    game_details = {
        "map": "Touch Grass",
        "map_preview_file": "touch_grass.png",
        "track_length": 3500,
        "wr_time": 47.23,
        "pb_time": 56.12,
    }
    game_started = waiting_room(game_details, False)
    
    # INFO: game_started will be FALSE if we should return to main menu, and TRUE if the game should start.
    
    if game_started:
        # TODO - start game
        pass
    else:
        main_menu() 
    """
    ################## ^^^ TESTS ^^^ ##################
    
    # MAIN:
    
    # see docstring for main_menu and other comments in that file for an explanation
    main_menu_result = main_menu()
    while not main_menu_result:
        main_menu_result = main_menu()
        
    # if loop broken, that means we are ready to move on to the live game screen.
    # TODO - start live game    
    print("enter live game")
    
    try:
        # Gracefully close the socket connection to prevent ghost client on server side
        GameManager.socket_man.socket.close()
    except: pass

if __name__ == "__main__":
    start_program()