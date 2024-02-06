# code borrowed from https://www.pygame.org/wiki/Spritesheet?parent=CookBook 
# I've added a couple modifications to frames so instead of it counting in tics it causes the program to sleep 
# for the speficied amount of time

import pygame
import os
from spritesheet import spritesheet
from time import sleep

from CONSTANTS import *
from game_map import GameMap

orig_width = 500
orig_height = 450

width = 1200 
height = 480

sprite_fp = lambda name: os.path.join(os.path.dirname(__file__), ROAD_FRAMES_DIR + str(name))

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
        ss = spritesheet(foldername)
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
        """
        Returns the next image in the sequence. If the end of the sequence is reached, and the loop flag is set, it will start over. If the loop flag is not set, it will return None.
        """
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

class RoadAnimator:
    """
    Provides the road image to blit on the screen depending on the car's `x` position.
    
    For example, if we are currently on a `CurveSegment`, this will keep returning curved road images.
    
    Framerate is calculated based on car speed. (moving faster = faster animation)
    """
    
    def __init__(self, gamemap: GameMap):
        """
        Constructs an auto-looping sprite animator.
        
        @param `dirpath`: Path to the folder containing the images
        @param `image_count`: Number of images in the folder
        @param `rect`: (x, y, width, height) to crop the images to. 
        It seems, since the sprite png's are 500x450, this value should be set to `(0, 0, 500, 450)` to get the full image.
        """
        self.game_map = gamemap
        
        # use for calculating animation frames
        self.last_frame_x_pos = 0
        
        self.frame_in_use = 0
        """ Will be either 0 or 1, since each angle of road only has two frames which we alternate between. """
        
        self.ordered_sprites = [spritesheet(sprite_fp(angle)) for angle in range(-70, 80, 10)]
        """
        The collection where we pull our animations. This is what the return value of `road_curvature_factor` points to.
        """
        
    def sprite_from_angle(self, angle: int) -> spritesheet:
        """
        Returns the index of the spritesheet to use based on the angle.
        
        We have spritesheets for tracks of of -70deg -> 70deg, in intervals of 10deg.
        
        This function returns 0 for any a<-70, 1 for -70<a<-60, and so on up until 15 for 70<a.
        """
        angle = max(-70, min(70, angle)) # clamp to -80, 80
        return self.ordered_sprites[int((angle + 70) / 10)]

    def get_next(self, x_pos: float) -> pygame.Surface:
        """
        Returns the next frame of the animation based on the car's current location.
        
        @param `x_pos`: The x position of the car.   
             
        Blit this onto the screen continuously to animate.
        """
        
        # Animate differently based on current spritesheet.
        sprite = self.sprite_from_angle(self.game_map.angle_at(x_pos))
        
        # check if we've moved enough to advance to the next frame
        if x_pos > self.last_frame_x_pos + METERS_PER_ANIMATION_FRAME:
            # move to the next image
            self.frame_in_use = (self.frame_in_use + 1) % FRAMES_PER_ANGLE
            self.last_frame_x_pos = x_pos
        
        img = sprite.frames[self.frame_in_use]
        
        img = pygame.transform.scale(img, (width, height))
        img.convert_alpha()
        return img