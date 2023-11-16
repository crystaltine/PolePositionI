import pygame, sys
from pygame.locals import*

class User(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        #self.image = pygame.image.load("Player.png") -> load in actual img later
        #self.rect = self.image.get_rect()
        self.rect = Rect(100, 100, 50, 50)
        self.rect.center = (160, 520) #also fix num vals later
        self.angle = 0 #degrees from center of map

    def update():
        #general stuff and display speed and other variables
        pass

    def get_speed():
        pass
    
    def is_collision():
        pass
    
    def get_map_pos():
        pass

    def set_angle():
        #update angle when car moves
        pass

    def get_angle():
         #for background to know how much to change
        pass
