from game_manager import GameManager
from screens.cant_connect import cant_connect
from screens.main_menu import main_menu
from requests_handler import HTTPManager

def start_program():
    """
    This should be run on app start. Creates connections, decides which screen to send the user to
    (Main menu or connecting... screen)
    """

    try:
        GameManager.socket_man.connect()
    except ConnectionRefusedError:
        cant_connect()

    GameManager.http_man = HTTPManager(GameManager.socket_man.client_id)
    
    # All is good, send to title screen!
    main_menu()

if __name__ == "__main__":
    start_program()