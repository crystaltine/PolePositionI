from managers import GameManager, init_managers

from screens.main_menu import main_menu
from screens.countdown import countdown
from screens.live_game import live_game
from screens.game_end import game_end

def start_program():
    """
    This should be run on app start. Creates connections, decides which screen to send the user to
    (Main menu or connecting... screen)
    """
    
    init_managers()
    
    # see docstring for main_menu and other comments in that file for an explanation
    # tldr - main menu will return False if we should stay on it, and True if we should proceed to the next screen
    main_menu_result = main_menu()
    while not main_menu_result:
        main_menu_result = main_menu()
        
    # if loop broken, that means we are ready to move on to the countdown screen.
    countdown()
    live_game_result = live_game()
    
    if live_game_result == 2: # this is a code to move to the end screen
        game_end(GameManager.leaderboard_data)

    GameManager.socket_man.stop_listening()
    del GameManager.game_renderer.world

if __name__ == "__main__":
    while True:
        start_program()