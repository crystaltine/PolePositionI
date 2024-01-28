from game_manager import GameManager

from screens.main_menu import main_menu
from screens.countdown import countdown
from screens.live_game import live_game

def start_program():
    """
    This should be run on app start. Creates connections, decides which screen to send the user to
    (Main menu or connecting... screen)
    """
    
    # see docstring for main_menu and other comments in that file for an explanation
    # tldr - main menu will return False if we should stay on it, and True if we should proceed to the next screen
    main_menu_result = main_menu()
    while not main_menu_result:
        main_menu_result = main_menu()
        
    # if loop broken, that means we are ready to move on to the countdown screen.
    countdown()
    live_game()
    
    try:
        # Gracefully close the socket connection to prevent ghost client on server side
        GameManager.socket_man.socket.close()
    except: pass

if __name__ == "__main__":
    start_program()