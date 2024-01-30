# code borrowed from https://www.pygame.org/wiki/Spritesheet?parent=CookBook 
# I've added a couple modifications to frames so instead of it counting in tics it causes the program to sleep 
# for the speficied amount of time

import spritesheet
from time import sleep

class SpriteStripAnim(object):
    """sprite strip animator
    
    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    """
    def __init__(self, foldername, rect, count, colorkey = None, loop=False, frames=0.041):
        """construct a SpriteStripAnim
        
        filename, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.
        
        loop is a boolean that, when True, causes the next() method to
        loop. If False returns None.
        
        frames is the number of seconds to return the same image before
        the iterator advances to the next image.
        """
        self.foldername = foldername
        ss = spritesheet.spritesheet(foldername)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
    def iter(self):
        self.i = 0
        self.f = self.frames
        return self
    def next(self):
        self.i += 1
        if self.i >= len(self.images):
            self.i = 0
            if not self.loop:
                return None
        image = self.images[self.i]
        sleep(self.frames)
        return image
    def current(self):
        image = self.images[self.i]
        return image
    def __add__(self, ss):
        self.images.extend(ss.images)
        return self
    def set_frames(self, frames):
        self.frames = frames