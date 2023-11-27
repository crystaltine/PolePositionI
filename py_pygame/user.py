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
        event = pygame.event()
        keypress = None
        if event.type = pygame.KEYDOWN:
            keypress = 1
        if event.type = pygame.KEYUP:
            keypress = 0

        #working on keyinpuyt use this future me https://stackoverflow.com/questions/16044229/how-to-get-keyboard-input-in-pygame 

        #if key[K_UP]
        #    keypress = 00
        #if key[K_DOWN]
        #    keypress = 00
        #if key[K_LEFT]
        #    keypress = 00
        #if key[K_DOWN]
        #    keypress = 00
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
