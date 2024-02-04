import pygame
import sys
#from requests_handler import capture_keypress_loop
from animator import SpriteStripAnim
import os
import datetime

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
backdrop = pygame.image.load(os.path.join(os.path.dirname(__file__), 'assets','mountains_img.png')).convert_alpha()
#backdrop = pygame.transform.scale(backdrop, (width*2, height/5))
road_straight = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
curved_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved left'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
curved_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved right'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
left_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\left centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)
right_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\right centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)
turning_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning left'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)
turning_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning right'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)

#create explosion
boom = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\collision explosino'), (0, 0, width, height), 5, -1, False, 0.25)

#all linked animations for the full track
roadpaths = [
    road_straight, 
    turning_left,
    curved_left, 
    left_centering,
    road_straight, 
    turning_right,
    curved_right,
    right_centering,
    road_straight,
    turning_left,
    curved_left, 
    left_centering,
    road_straight,
    turning_right,
    curved_right,
    right_centering,
    road_straight,
    turning_left,
    curved_left, 
    left_centering,
    road_straight
]
roadpaths_index = 0
roadpaths[roadpaths_index].iter()
road_image = roadpaths[roadpaths_index].current()
road_image = pygame.transform.scale_by(road_image, (2.4, 1.945))

menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     

road_state = 0

start_time = datetime.datetime.now()
game_start_time = start_time.minute + start_time.second*100

is_boom = False
boom.iter()
boom_frame = boom.current()

#game state 
while True:
    screen.blit(grass, (0, 2*height/5))
    screen.blit(backdrop, (0, 0)) #height/5
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_RIGHT:
                roadpaths_index += 1
                if roadpaths_index >= len(roadpaths):
                    roadpaths_index = 0

    screen.blit(road_image, (0, -6.9*height/5))        

    pygame.display.flip()
    road_image = roadpaths[roadpaths_index].next()      
    current_time = datetime.datetime.now()
    game_current_time = current_time.minute + current_time.second*100
    if road_image is None:
        roadpaths_index += 1
        roadpaths[roadpaths_index].iter()
        road_image = roadpaths[roadpaths_index].current()
    road_image = pygame.transform.scale_by(road_image, (2.4, 1.945))
