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
        keys: list[bool] = [False, False, False, False]
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
        
        delta_time_s = (time_ns() - self.last_update_timestamp) / 1e9
        
        # update angle
        self.angle += (self.key_presses[3] - self.key_presses[2]) * 50 * delta_time_s
        
        # TODO - these equation are tweakable (maybe even make deceleration quadratic?)
        # if w is held down, set x acceleration to -1/(20*vel_x) + 5 <- ensures no acc at v=100m/s
        # if s is held down, set x acceleration to -1/(5*vel_x) <- ensures no deacc at v=0m/s
        # if neither or both, set x acceleration to 0
        
        if self.key_presses[0] and not self.key_presses[1]:
            self.acc = -self.vel/20 + 5
        elif self.key_presses[1] and not self.key_presses[0]:
            self.acc = -self.vel/5
        else:
            self.acc = 0

        # update velocity
        self.vel += self.acc * delta_time_s
        
        # update positions
        relative_angle = self.angle - self.gamemap.angle_at(self.pos[0])
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
          keys: [forward: bool, backward: bool, left: bool, right: bool]
        },
        ```
        """
        
        return {
            "pos": self.pos,
            "vel": self.vel,
            "acc": self.acc,
            "angle": self.angle%360,
            "hitbox_radius": self.hitbox_radius,
            "keys": self.key_presses
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
          keys: [forward: bool, backward: bool, left: bool, right: bool]
        },
        ```
        """
        
        self.pos = data["pos"]
        self.vel = data["vel"]
        self.acc = data["acc"]
        self.angle = data["angle"]%360
        self.hitbox_radius = data["hitbox_radius"]
        self.key_presses = data["keys"]
        
        self.last_update_timestamp = time_ns()