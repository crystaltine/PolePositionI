import pygame
import sys
import random
from game.requests_handler import capture_keypress_loop
import spritesheet
from sprite_strip_anim import SpriteStripAnim

pygame.init()

running = True
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = pygame.display.get_desktop_sizes()[0][0]
height = pygame.display.get_desktop_sizes()[0][1]

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
font = pygame.font.Font('freesansbold.ttf', 32)
#grass = pygame.image.load('../../assets/grasse.png')
#grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
#mtns = pygame.image.load('..\\..\\assets\\mtns.png')
#mtns = pygame.transform.scale(mtns, (width*2, height/5))
#road = pygame.image.load('straightRoad.gif')
road = SpriteStripAnim('straightRoad.gif', (0, -height/5, width, 4*height/3), 12, 4, False, 1000)
#road = pygame.transform.scale(road, (width, 4*height/3))
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
        #screen.blit(grass, (0, 2*height/5))
        #screen.blit(mtns, (0, height/5))
        #screen.blit(road, (0, -height/5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # escape button works 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
        pygame.display.update()
   
pygame.quit()
sys.exit()