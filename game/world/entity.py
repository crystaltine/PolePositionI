from typing import List, TYPE_CHECKING
from time import time_ns
import math

if TYPE_CHECKING:
    from game_map import GameMap

class Entity:
    """
    Represents a player's car.
    Has pos, vel, acc, angle, and a circular hitbox with a certain radius.
    
    `pos` is a list of two floats: `[distance along track, offset from track center]`
    
    `vel` and `acc` are both scalars, and `angle` is in degrees.
    `angle` controls how `vel` affects `pos`.
    
    When a track is curved, uses the relative angle 
    (how far off the player is turned away from the center of the track)
    to calculate the new position.
    
    ### This must effectively be the same as on the server side
    ^ just with a few server-related things removed, like client objects
    """
    def __init__(
        self,
        name: str,
        color: str,
        gamemap: 'GameMap',
        pos: List[float],
        vel: float = 0,
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: List[bool] = [False, False, False, False],
        is_crashed: bool = False
        ) -> None:
        
        #instance variables 
        self.name = name
        self.color = color
        self.gamemap = gamemap
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.angle = angle%360
        self.hitbox_radius = hitbox_radius
        
        self.last_update_timestamp = time_ns()
        
        self.is_crashed = is_crashed # used to render explosion animation for enemies
        
        self.crash_end_timestamp = 0 # only used for the us entity
    
        # False = key is not held down, True = key is held down
        # Use this to update acceleration and angle
        # w = +acc, s = -acc, a = +angle, d = -angle
        self.key_presses = keys.copy()
        """ `[forward, backward, left, right]` """
        
    def update(self):
        """
        Updates physics, including position, velocity, acceleration, and angle.
        
        If the track is curved at this entity's x-position, 
        then position is updated with the entity's relative angle (`self.angle - track_angle`)
        
        For example, if the entity has an angle of -10 degrees (turned left), 
        but the track is curved at 30 degrees (going right) at that x-pos,
        then position is updated similar to as follows:
        
        ```python
        x_position += velocity * cos(radians(-10-30)) * delta_time_s   
        y_position += velocity * sin(radians(-10-30)) * delta_time_s
        ```    
        
        which would result in them drifting to the left side of the track.
        
        Should be run on every server tick (for now, 24tps) - see `../CONSTANTS.py`
        """
        
        # if we are in a crash, don't update
        time_until_crash_end = self.crash_end_timestamp - time_ns()/1e9
        if time_until_crash_end > 0:
            
            # set all keys to False
            self.key_presses = [False, False, False, False]
            
            self.last_update_timestamp = time_ns()
            return
        
        delta_time_s = (time_ns() - self.last_update_timestamp) / 1e9
        
        # update angle
        turn_resistance_factor = -(0.01*self.vel-1)**2 + 1
        self.angle += (self.key_presses[3] - self.key_presses[2]) * 50 * turn_resistance_factor * delta_time_s
        self.angle %= 360
        
        # clamp angle to 270-360 and 0-90 only
        if self.angle>=180 and self.angle<270:
            self.angle = 270
        elif self.angle<180 and self.angle>90:
            self.angle = 90
        
        # if w is held down, set x acceleration to 10- sqrt vel <- ensures no acc at v=100m/s
        # if s is held down, set x acceleration to -10, other handling ensures that velocity will stay between 0 and 100 m/s
        # if neither or both, set x acceleration to - sqrt vel <- simulates drag and high air resistance at higher speeds
        if self.key_presses[1] and not self.key_presses[0]:
            self.acc = -10 
        elif self.key_presses[0] and not self.key_presses[1]:
            self.acc = 10 - math.sqrt(self.vel)
        else:
            self.acc = -math.sqrt(self.vel)

        # update velocity with with methods to guarantee it's within the ranges of 0-100
        self.vel = max(0, min(self.vel + self.acc * delta_time_s, 100))
        
        #adjusting angular accel value to slow turning at higher speeds
        denominator = 0.4 * self.vel + 2.22 
        #value that changes how much a person can turn based on speed 
        angular_accel = 10/denominator + .5 
        # update positions
        #angle change now involves speed with mod 360 to reset angle 
        relative_angle = (self.angle + angular_accel * delta_time_s - self.gamemap.angle_at(self.pos[0])) % 360
        self.pos[0] += self.vel * math.cos(math.radians(relative_angle)) * delta_time_s
        self.pos[1] += self.vel * math.sin(math.radians(relative_angle)) * delta_time_s
        
        # update timestamp
        self.last_update_timestamp = time_ns()
    
    def get_physics_data(self) -> dict:
        """
        Return all physical data in a dict of the following format:
        
        ```typescript
        {
          pos: [pos_x: number, pos_y: number],
          vel: number,
          acc: number,
          angle: number, // in degrees
          hitbox_radius: number,
          keys: [forward: bool, backward: bool, left: bool, right: bool],
          is_crashed: bool
        },
        ```
        """
        
        return {
            "pos": self.pos,
            "vel": self.vel,
            "acc": self.acc,
            "angle": self.angle%360,
            "hitbox_radius": self.hitbox_radius,
            "keys": self.key_presses,
            "is_crashed": self.is_crashed
        }
    
    def get_progress(self) -> float:
        """
        Returns the percentage of the track that the player has completed.
        
        All values returned are in the range [0, 1].
        """
        
        return self.pos[0] / self.gamemap.map_data['length']
    
    def set_physics(self, data: dict) -> None:
        """
        Set and override the current physics data. This should only be used with server data (or for testing)
        
        `data` must be a dict in the same format as the one returned by `get_physics_data()`, which looks like this:
        
        ```typescript
        {
          pos: [pos_x: number, pos_y: number],
          vel: number,
          acc: number,
          angle: number, // in degrees
          hitbox_radius: number,
          keys: [forward: bool, backward: bool, left: bool, right: bool],
          is_crashed: bool
        },
        ```
        """
        
        self.pos = data["pos"]
        self.vel = data["vel"]
        self.acc = data["acc"]
        self.angle = data["angle"]%360
        self.hitbox_radius = data["hitbox_radius"]
        self.key_presses = data["keys"]
        self.is_crashed = data["is_crashed"]
        
        self.last_update_timestamp = time_ns()