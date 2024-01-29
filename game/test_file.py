import pygame
import sys
import random
#from requests_handler import capture_keypress_loop
import spritesheet
from sprite_strip_anim import SpriteStripAnim
import os
import datetime
from time import sleep

pygame.init()

SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 1200 #2.4
height = 720 #1.6

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load(os.path.join(os.path.dirname(__file__), 'assets','grass.png')).convert_alpha()
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load(os.path.join(os.path.dirname(__file__), 'assets','mtns.png')).convert_alpha()
mtns = pygame.transform.scale(mtns, (width*2, height/5))
road = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
curved_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved left'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
curved_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved right'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
left_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\left centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.08)
right_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\right centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.125)
turning_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning left'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)
turning_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning right'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.125)

roadpaths = [
    road, 
    turning_right,
    curved_right, 
    right_centering,
    road
]
roadpaths_index = 0
roadpaths[roadpaths_index].iter()
road_state = roadpaths[roadpaths_index].current()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))

road_state = roadpaths[roadpaths_index].next()
road_state = roadpaths[roadpaths_index].next()

screen.blit(road_state, (0, -6*height/5))        
pygame.display.flip()
sleep(1)
road_state = roadpaths[roadpaths_index].next()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))
screen.blit(road_state, (0, -6*height/5))        
pygame.display.flip()
sleep(1)
road_state = roadpaths[roadpaths_index].next()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))
screen.blit(road_state, (0, -6*height/5))        
pygame.display.flip()
sleep(1)
road_state = roadpaths[roadpaths_index].next()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))
screen.blit(road_state, (0, -6*height/5))        
pygame.display.flip()
sleep(1)
road_state = roadpaths[roadpaths_index].next()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))



menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     

start_time = datetime.datetime.now()
start = start_time.minute * 10 + start_time.second

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
    screen.blit(road_state, (0, -6*height/5))        
    pygame.display.flip()
    road_state = roadpaths[roadpaths_index].next()
    road_state = pygame.transform.scale_by(road_state, (2.4, 1.82)) #2900, 653
    sleep(0.1)
    current_time = datetime.datetime.now()
    #current = current_time.minute * 100 + current_time.second
    #if not(current - start < 8) and roadpaths_index < 1:
    #    roadpaths_index += 1
    #elif (not current - start < 9) and roadpaths_index < 2:
    #    roadpaths_index +=1
    