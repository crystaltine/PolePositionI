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

 
    
    # All is good, send to title screen!
    main_menu()

if __name__ == "__main__":
    start_program()