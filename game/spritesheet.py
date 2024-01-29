# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using 
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)
# I've taken the taken code from https://www.pygame.org/wiki/Spritesheet?parent=CookBook 
# and added a couple modifications of my own to the error message

import pygame
import os

class spritesheet(object):
    def __init__(self, foldername):
        self.frames = []
        for file in os.listdir(foldername):
            file_path = os.path.join(foldername, file)
            self.frames.append(pygame.image.load(file_path).convert())
        #try:
        #    self.sheet = pygame.image.load(foldername).convert()
        #except pygame.error:
        #    print('Unable to load spritesheet image:' + foldername)
        #    raise SystemExit
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, index, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.frames[index], (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rects[i], i, colorkey) for i in range (len(rects))]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
