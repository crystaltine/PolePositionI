import pygame
import sys
from button import Button
pygame.init()

running = True
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 640
height = 480
screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")

font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load('grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load('mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))


menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     


        

def print_hello():
    print("hello")
            

def start_menu(): # game screen
#call object instances outside the loop
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))


        PLAY_BUTTON = Button(pos=(300,200), text_input="PLAY", font=font, base_color="#d7fcd4", hovering_color="White", image=pygame.image.load("assets/Play Rect.png"))

        PLAY_BUTTON.changeColor(mouse_pos)
        PLAY_BUTTON.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(mouse_pos):
                    print("lol")
        
        pygame.display.update()

        #key numbers for keydowbs binary onkeyevent -> send to server
        #up: 00
        #down: 01
        #left: 10
        #right: 11

        #keydown: 1##
        #keyup: 0##

start_menu()










