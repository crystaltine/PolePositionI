import pygame
import sys

pygame.init()

running = True
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = pygame.display.get_desktop_sizes()[0][0]
height = pygame.display.get_desktop_sizes()[0][1]

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
# size = pygame.display.get_desktop_sizes()
font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load('grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load('mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))
#FPS = pygame.time.Clock()
#FPS.tick(24) #moved timer into loop 
# player = User(Sprite) insert sprite later

menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     

def main_menu(): # start screen 
    while running: 
        mouse_pos = pygame.mouse.get_pos()
        screen.fill("white")
        

        
            

def play(): # game screen
#call object instances outside the loop
    while running:
        
        # start_screen(True)
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

   
play()