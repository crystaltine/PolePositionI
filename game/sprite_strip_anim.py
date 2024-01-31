# code borrowed from https://www.pygame.org/wiki/Spritesheet?parent=CookBook 
# I've added a couple modifications to frames so instead of it counting in tics it causes the program to sleep 
# for the speficied amount of time

import pygame
import os
from spritesheet import spritesheet
from time import sleep

from CONSTANTS import METERS_PER_ANIMATION_FRAME
from game_map import GameMap

orig_width = 500
orig_height = 450

width = 1200 
height = 480

sprite_fp = lambda name: os.path.join(os.path.dirname(__file__), 'assets\\road frames\\' + name)

road_straight = spritesheet(sprite_fp("straight road"))
curved_left = spritesheet(sprite_fp("curved left"))
curved_right = spritesheet(sprite_fp("curved right"))
left_centering = spritesheet(sprite_fp("left centering"))
right_centering = spritesheet(sprite_fp("right centering"))
turning_left = spritesheet(sprite_fp("turning left"))
turning_right = spritesheet(sprite_fp("turning right"))

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
        self.image_index = 0
        
        # use for calculating animation frames
        self.last_frame_x_pos = 0
        
        self.sprite_percentage = 0
        """ Stores how far we are into the current angle change. For example, if we are halfway between `start` and `q1` (see `sprite_to_use`), this will be 0.5. """
        
    def sprite_to_use(self, x_pos: float) -> spritesheet:
        """
        Returns the spritesheet to use at the current x-position based on the map this animator is attached to.
        
        For example, if the road is currently straight at `x_pos`, this will return `road_straight`.
        
        If the road is curved, we use our position on a `CurveSegment` to determine which spritesheet to use.
        """
        
        curr_curvesegment = self.game_map.curvesegment_at(x_pos)
        
        if curr_curvesegment is None:
            return road_straight
    
        curvesegment_rampup_length = curr_curvesegment.mid_x - curr_curvesegment.start_x
        curvesegment_rampdown_length = curr_curvesegment.end_x - curr_curvesegment.mid_x
        
        start = curr_curvesegment.start_x
        q1 = curr_curvesegment.mid_x - curvesegment_rampup_length/2
        q3 = curr_curvesegment.mid_x + curvesegment_rampdown_length/2
        end = curr_curvesegment.end_x

        # if pos is between start and halfway from start-mid, use turning
        # if pos is between halfway to start-mid and halfway from mid-end, use full curve
        # if pos is between halfway to mid-end and end, use centering

        if curr_curvesegment.theta_f > 0: # rightward
            if x_pos > start and x_pos < q1:
                self.sprite_percentage = (x_pos - start) / (q1 - start)
                return turning_right
            elif x_pos > q1 and x_pos < q3:
                # no sprite percentage needed here, since all curved_right images have the same angle
                return curved_right
            elif x_pos > q3 and x_pos < end:
                self.sprite_percentage = (x_pos - q3) / (end - q3)
                return right_centering
            
        else: # leftward
            if x_pos > start and x_pos < q1:
                self.sprite_percentage = (x_pos - start) / (q1 - start)
                return turning_left
            elif x_pos > q1 and x_pos < q3:
                # no sprite percentage needed here, since all curved_left images have the same angle
                return curved_left
            elif x_pos > q3 and x_pos < end:
                self.sprite_percentage = (x_pos - q3) / (end - q3)
                return left_centering

    def index_of_turning_sprite(self, x_pos: float) -> int:
        """
        If we are currently on one of the following spritesheets:
        - `turning_left`
        - `turning_right`
        - `centering_left`
        - `centering_right`
        
        Then this function returns the index of the spritesheet's images to use. 
        This is because the images in these spritesheets are all at different angles, so
        we have to use the correct one based on how curved the track is at the current position.       
        
        For example, let's say we are at x=900, and on a `CurveSegment` that turns left, starts at x=800, and peaks at x=1000.
        Then, we would use the middle image in `turning_left` (since it's 50% of the way through the curve).
        """ 
        
        # IMPORTANT - turning/centering sprites have 8 images.
        
        idx = int(self.sprite_percentage * 8)
        return idx        

    def get_next(self, x_pos: float) -> pygame.Surface:
        """
        Returns the next frame of the animation based on the car's current location.
        
        @param `x_pos`: The x position of the car.   
             
        Blit this onto the screen continuously to animate.
        """
        
        # Animate differently based on current spritesheet.
        
        sprite = self.sprite_to_use(x_pos)
        
        # if the road is straight or fully curved, we can just use the spritesheet's frames
        if sprite in [road_straight, curved_left, curved_right]:
            # check if we've moved enough to advance to the next frame
            if x_pos > self.last_frame_x_pos + METERS_PER_ANIMATION_FRAME:
                # move to the next image
                self.image_index = (self.image_index + 1) % len(sprite.frames)
                self.last_frame_x_pos = x_pos
            
            img = sprite.frames[self.image_index]
            
            img = pygame.transform.scale(img, (width, height))
            img.convert_alpha()
            return img
        
        # If the road's curvature is changing, we have to calculate the index of the spritesheet's frames to use.
        else:
            # calculate the index of the spritesheet's frames to use
            index = self.index_of_turning_sprite(x_pos)
            img = sprite.frames[index]
            img = pygame.transform.scale(img, (width, height))
        
        img.convert_alpha()
        return img
    