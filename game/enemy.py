import pygame, sys
from pygame.locals import*

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        #self.image = pygame.image.load("Player.png") -> load in actual img later
        #self.rect = self.image.get_rect()
        self.rect = Rect(100, 100, 50, 50)
        self.rect.center = (160, 520) #also fix num vals later

    def update():
        pass

    def get_distance(user_pos):
        #pythagorean with user pos and get_map_pos to get dist from user
        pass
    
    def get_size():
        #user distance to set size of sprite
        pass

    def get_map_pos():
        pass