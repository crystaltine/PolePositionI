import pygame
import sys

# TODO - these import scopes might have to be changed depending on directory structure
from elements.button import Button
from elements.input import Input

from request_manager import SocketManager, HTTPManager
from CONSTANTS import FONT, BUTTON_LARGE, BUTTON_MEDIUM

#pygame.init() - initialized in CONSTANTS.py

running = True
in_game = False
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 1200
height = 720
screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")

grass = pygame.image.load('./game/assets/grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load('./game/assets/mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))

logo_img = pygame.image.load('./game/assets/logo.png')

# Buttons
CREATE_GAME_BUTTON = Button(pos=(340,400), display_text="CREATE GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_LARGE)

JOIN_MULTIPLAYER_INPUT = Input(x=340, y=480, w=240, h=60, text="")
JOIN_MULTIPLAYER_BUTTON = Button(pos=(600, 480), display_text="JOIN GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

SETTINGS_BUTTON = Button(pos=(340,560), display_text="SETTINGS", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)
QUIT_BUTTON = Button(pos=(600,560), display_text="QUIT GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)
# Initiate connections with server
socket_man = SocketManager()
http_man = HTTPManager(socket_man.client_id)

def start_menu(): # game screen
#call object instances outside the loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))
        
        # logo is 800x300, center it at (200, 50)
        screen.blit(logo_img, (200, 50))

        CREATE_GAME_BUTTON.changeColor(mouse_pos)
        CREATE_GAME_BUTTON.update(screen)

        JOIN_MULTIPLAYER_INPUT.draw(screen)
        JOIN_MULTIPLAYER_BUTTON.changeColor(mouse_pos)
        JOIN_MULTIPLAYER_BUTTON.update(screen)
        
        SETTINGS_BUTTON.changeColor(mouse_pos)
        SETTINGS_BUTTON.update(screen)
        
        QUIT_BUTTON.changeColor(mouse_pos)
        QUIT_BUTTON.update(screen)
        
        for event in pygame.event.get():
            
            # for typing in the input box
            JOIN_MULTIPLAYER_INPUT.handle_event(event)
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CREATE_GAME_BUTTON.is_hovering(mouse_pos):
                    res = http_man.create_room()
                    
                    if not res['success']:
                        print("Error creating room!!!", res.get('message'))
                        # TODO - display message on screen, maybe a little text blurb under the button that says the message
                    
                    else:
                        print("Room created successfully! Code:", res.get('code'))
                        # TODO - display the waiting lobby
                    
                if JOIN_MULTIPLAYER_BUTTON.is_hovering(mouse_pos):
                    res = http_man.join_room(JOIN_MULTIPLAYER_INPUT.text)
                    
                    if not res['success']:
                        print("Error joining room!!!", res.get('message'))
                        # TODO - display message on screen, maybe a little text blurb under the input box that says the message
                    
                    else:
                        print("Room joined successfully! Code:", res.get('code'))
                        # TODO - display the waiting lobby
                    
                if SETTINGS_BUTTON.is_hovering(mouse_pos):
                    pass # TODO - settings menu?
                
                if QUIT_BUTTON.is_hovering(mouse_pos):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()

def game():
    while True:
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

def create_room():
    while True:
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

def join_room():
    while True:
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


#key numbers for keydowbs binary onkeyevent -> send to server
#up: 00
#down: 01
#left: 10
#right: 11

#keydown: 1##
#keyup: 0##

start_menu()