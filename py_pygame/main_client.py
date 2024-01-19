import pygame
import sys
from button import Button
pygame.init()

running = True
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 800
height = 600
screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")

font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load('grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load('mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))




            

def start_menu(): # game screen
#call object instances outside the loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))


        PLAY_SINGLEPLAYER_BUTTON = Button(pos=(100,400), text_input="PLAY", font=font, base_color="#d7fcd4", hovering_color="White", image=pygame.image.load("assets/Play Rect.png"))
        PLAY_SINGLEPLAYER_BUTTON.changeColor(mouse_pos)
        PLAY_SINGLEPLAYER_BUTTON.update(screen)


        START_MULTIPLAYER_BUTTON = Button(pos=(350,400), text_input="MAKE ROOM", font=font, base_color="#d7fcd4", hovering_color="White", image=pygame.image.load("assets/Play Rect.png"))
        START_MULTIPLAYER_BUTTON.changeColor(mouse_pos)
        START_MULTIPLAYER_BUTTON.update(screen)

        JOIN_MULTIPLAYER_BUTTON = Button(pos=(600,400), text_input="JOIN ROOM", font=font, base_color="#d7fcd4", hovering_color="White", image=pygame.image.load("assets/Play Rect.png"))
        JOIN_MULTIPLAYER_BUTTON.changeColor(mouse_pos)
        JOIN_MULTIPLAYER_BUTTON.update(screen)




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_SINGLEPLAYER_BUTTON.checkForInput(mouse_pos):
                    game()
                if START_MULTIPLAYER_BUTTON.checkForInput(mouse_pos):
                    create_room()
                if JOIN_MULTIPLAYER_BUTTON.checkForInput(mouse_pos):
                    join_room()
        
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










