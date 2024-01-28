import pygame
import sys
import random
#from requests_handler import capture_keypress_loop
import spritesheet
from sprite_strip_anim import SpriteStripAnim
import os

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
road = []
curved_left = []
curved_right = []
left_centering = []
right_centering = []
turning_left = []
turning_right = []
for img in range(12):
    if img < 11:
        road.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road', str(img) + ' 06-53-01.png'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041))
        curved_left.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved left', str(img) + ' 06-50-02.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        curved_right.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved right', str(img) + ' 06-50-35.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
    else:
        road.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road', str(img) + ' 06-53-01.png'), (0, -3*height/5, width, 4*height/3), 12, -1, False, 0.041))
        curved_left.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved left', str(img) + ' 06-50-02.png'), (0, -height/5, width, 4*height/3), 12, -1, False, 0.041))
        curved_right.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved right', str(img) + ' 06-50-35.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))

for img in range(8):
    if img < 7:
        left_centering.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\left centering', str(img) + ' 06-50-52.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        right_centering.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\right centering', str(img) + ' 06-52-48.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        turning_left.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning left', str(img) + ' 06-52-17.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        turning_right.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning right', str(img) + ' 06-51-52.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
    else:
        left_centering.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\left centering', str(img) + ' 06-50-52.png'), (0, -height/5, width, 4*height/3), 12, -1, False, 0.041))
        right_centering.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\right centering', str(img) + ' 06-52-48.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        turning_left.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning left', str(img) + ' 06-52-17.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))
        turning_right.append(SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning right', str(img) + ' 06-51-52.png'), (0, -height/5, width, 4*height/3), 12, -1, True, 0.041))

roadpaths = [
    road, 
    turning_right,
    curved_right, 
    right_centering,
    road
]
current_loop = 0
road[current_loop].iter()
road_state = road[current_loop].next()
road_state = pygame.transform.scale_by(road_state, (2.4, 1.82))

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
    road[current_loop].next()
    screen.blit(road_state, (0, -6*height/5))        
    pygame.display.flip()
    road_state = road[current_loop].next()
    road_state = pygame.transform.scale_by(road_state, (2.4, 1.82)) #2900, 653