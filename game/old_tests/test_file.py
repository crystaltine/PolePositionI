import pygame
import sys
import random
#from game.requests_handler import capture_keypress_loop
import spritesheet
from sprite_strip_anim import SpriteStripAnim
import os

pygame.init()

SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 1200
height = 720

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load(os.path.join(os.path.dirname(__file__), 'assets','grass.png')).convert_alpha()
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load(os.path.join(os.path.dirname(__file__), 'assets','mtns.png')).convert_alpha()
mtns = pygame.transform.scale(mtns, (width*2, height/5))
road = []
for img in range(12):
    road.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road', str(img) + ' 06-53-01.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 100000000))
roadpaths = [
    road,
    SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets','turningLeft.gif'), (0, -height/5, width, 4*height/3), 8, -1, True, 1),
    SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets','curvedLeft.gif'), (0, -height/5, width, 4*height/3), 12, -1, True, 1),
    SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets','leftCentering.gif'), (0, -height/5, width, 4*height/3), 8, -1, True, 1),
    road
]
current_loop = 0
road[current_loop].iter()
road_state = road[current_loop].next()

menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     

#def main_menu(): # start screen 
#    while running: 
#        mouse_pos = pygame.mouse.get_pos()
#        screen.fill("white")


#call object instances outside the loop
while True:
    screen.blit(grass, (0, 2*height/5))
    screen.blit(mtns, (0, height/5))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
    current_loop += 1
    if current_loop >= len(road):
        current_loop = 0
    road[current_loop].iter()
    screen.blit(road_state, (0, -height/5))        
    pygame.display.flip()
    road_state = road[current_loop].next()