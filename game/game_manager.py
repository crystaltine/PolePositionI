import pygame
from typing import Union

from CONSTANTS import *
from elements.button import Button
from elements.input import Input
from requests_handler import SocketManager, HTTPManager

class GameManager:
    """
    A class that declares/scores all assets and resources used, such as screen, buttons, etc.
    
    Will implement functions that allow for quick display management.
    """
    
    # used solely for waiting room event callbacks. See game/screens/waiting_room.py for more info.
    waiting_room_game_started = False
    waiting_room_leave_game = False
    
    # both of these will be set when we join/create a room
    room_id: Union[None, str] = None
    our_username: str = None
    
    # Initiate connections with server
    socket_man = SocketManager()
    http_man: Union[None, HTTPManager] = None
    """ Will be set externally """
    
    # main assets
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    screen.fill(SKY_RGB)

    grass = pygame.image.load('./game/assets/grass.png')
    grass = pygame.transform.scale(grass, (int(WIDTH), int(2 * HEIGHT/3)))
    
    mtns = pygame.image.load('./game/assets/mountains_img.png')
    mtns = pygame.transform.scale(mtns, (WIDTH*2, HEIGHT-grass.get_height()))
    
    logo_img = pygame.image.load('./game/assets/logo.png')

    car = pygame.image.load('./game/assets/atariPolePosition-carStraight.png')

    # Buttons
    create_game_button = Button(pos=(340,400), display_text="CREATE GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_LARGE)

    join_game_input = Input(x=340, y=480, w=240, h=60, text="")
    join_game_button = Button(pos=(600, 480), display_text="JOIN GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    livegametest_button = Button(pos=(340,560), display_text="LIVEGAMETEST", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)
    quit_button = Button(pos=(600,560), display_text="QUIT", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    countdown_button = Button(pos=(600,560), display_text="READY?", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    # main menu extra text
    text_bottom_left = FONT_TINY.render(MAIN_MENU_BOTTOM_LEFT_TEXT, True, (0, 0, 0))
    text_bottom_right = FONT_TINY.render(MAIN_MENU_BOTTOM_RIGHT_TEXT, True, (0, 0, 0))
    
    @staticmethod
    def draw_static_background():
        """
        Draws non-animated grass and mountains on the screen.
        """
        GameManager.screen.blit(GameManager.grass, (0, HEIGHT - GameManager.grass.get_height()))
        GameManager.screen.blit(GameManager.mtns, (0, 0))
        
    @staticmethod
    def draw_logo(posx = 200, posy = 50, scale = 1):
        """
        Draws the logo on the screen, with customizable position and scale. posx and posy are the top left corner of the logo.
        
        For reference, the original logo is 800x300 pixels.
        """
        scaled_logo = GameManager.logo_img
        if scale != 1:
            scaled_logo = pygame.transform.scale(scaled_logo, (int(scaled_logo.get_width() * scale), int(scaled_logo.get_height() * scale)))
        
        GameManager.screen.blit(scaled_logo, (posx, posy))
        
    @staticmethod
    def draw_homescreen_text():
        GameManager.screen.blit(GameManager.text_bottom_left, (20, HEIGHT - FONT_SIZES["tiny"] - 20))
        GameManager.screen.blit(GameManager.text_bottom_right, (WIDTH - GameManager.text_bottom_right.get_width() - 20, HEIGHT - FONT_SIZES["tiny"] - 20))
     
    @staticmethod   
    def TitleScreen():
        """
        Draws the title screen background, logo, and text.
        """
        GameManager.draw_static_background()
        GameManager.draw_homescreen_text()
        GameManager.draw_logo()
        
    def loop_titlescreen_buttons():
        """
        Handles styling and hovering on main menu buttons/inputs. Run inside the game loop.
        Doesn't do anything about clicks - that's handled in the `main_menu` function.
        
        Affected elements:
        - create_game_button
        - join_game_input
        - join_game_button
        - livegametest_button
        - quit_button
        """
        GameManager.create_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.create_game_button.update(GameManager.screen)
        
        GameManager.join_game_input.draw(GameManager.screen)
        
        GameManager.join_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.join_game_button.update(GameManager.screen)
        
        GameManager.livegametest_button.changeColor(pygame.mouse.get_pos())
        GameManager.livegametest_button.update(GameManager.screen)
        
        GameManager.quit_button.changeColor(pygame.mouse.get_pos())
        GameManager.quit_button.update(GameManager.screen)
    
    def loop_countdown_button():
        GameManager.countdown_button.update(GameManager.screen)

    def draw_car():
        GameManager.screen.blit(GameManager.car, (340,560))