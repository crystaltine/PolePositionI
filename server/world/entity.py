import math
from typing import List, TYPE_CHECKING
from time import time_ns

from CONSTANTS import *
from game_map import GameMap

if TYPE_CHECKING:
    from client_room import Client

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
    
    ### This must effectively be the same as on the client side
    ^ just with a few extra things maybe, since we have to deal with client objects
    """
    def __init__(
        self,
        name: str,
        color: str,
        client: 'Client',
        gamemap: GameMap,
        pos: List[float],
        vel: float = 0,
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: List[bool] = [False, False, False, False]
        ) -> None:
        
        self.name = name
        self.color = color
        self.client = client
        self.gamemap = gamemap
        self.pos = pos
        """ `[distance along track, offset from track center]` """
        self.vel = vel
        self.acc = acc
        self.angle = angle%360
        self.hitbox_radius = hitbox_radius
        
        self.last_update_timestamp = time_ns()
        
        # False = key is not held down, True = key is held down
        # Use this to update acceleration and angle
        # w = +acc, s = -acc, a = +angle, d = -angle
        self.key_presses = keys.copy()
        """ `[forward, backward, left, right]` - see `./key_decoder.py` for more info."""

    def update_keys(self, keyid: int, down: bool) -> None:
        """
        `keyid`: 0=forward, 1=backward, 2=left, 3=right
        if `down` is True, then the key is being pressed down, otherwise it is being released
        
        This function does not update any physics; 
        that should be done in `update()`, which is only used by the `World` class.
        """
        
        self.key_presses[keyid] = down
    
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
        
        # MAJOR TODO - we need to implement some sort of curvature calculation that accumulates angle, 
        # since rn, the client can still turn in any direction but we're only storing the angle of the track
        
        # TODO - these equation are tweakable (maybe even make deceleration quadratic?)
        # if w is held down, set x acceleration to 10- sqrt vel <- ensures no acc at v=100m/s
        # if s is held down, set x acceleration to -10, other handling ensures that velocity will stay between 0 and 100 m/s
        # if neither or both, set x acceleration to - sqrt vel <- simulates drag and high air resistance at higher speeds
        if self.key_presses[1] and not self.key_presses[0]:
            self.acc = -10 
        elif self.key_presses[0] and not self.key_presses[1]:
            self.acc = 10 - math.sqrt(total_vel)
        else:

            self.acc = -math.sqrt(total_vel)

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
    
    def check_out_of_bounds(self) -> bool:
        """
        Checks if `|self.pos[1]| > OOB_LENIENCY + TRACK_WIDTH/2` (a little bit of leniency)
        
        Returns the result of the above statement.
        If `True`, calls `self.on_wall_collide()`. If `False`, does nothing more.
        """
        
        if abs(self.pos[1]) > OOB_LENIENCY + TRACK_WIDTH/2:
            self.on_wall_collide()
            return True
        
        return False
   
    def check_win(self) -> bool:
        """
        Returns if `self.pos[0] > self.gamemap.map_data['length']`
        
        If this returns `True`, then the player has won the game.
        """
        
        return self.pos[0] > self.gamemap.map_data['length']
    
    def get_progress(self) -> float:
        """
        Returns the percentage of the track that the player has completed.
        
        All values returned are in the range [0, 1].
        """
        
        return self.pos[0] / self.gamemap.map_data['length']
     
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
        
    def on_entity_collide(self, other: 'Entity', spawn_direction: str, end_timestamp: float) -> None:
        """
        Called when this entity collides, but it must be WITH ANOTHER ENTITY.
        
        @param `spawn_direction` - either 'left' or 'right'.
        We don't want them spawning on top of each other,
        so left spawns at pos[1]=-MAP_WIDTH/5 and right spawns at pos[1]=MAP_WIDTH/5
        """
        
        # new physics: set velocity to 0, set acceleration to 0, set angle to track angle, 
        # and set y_pos to what's specified in `spawn_direction`
        
        y_pos_multiplier = -1 if spawn_direction=='left' else 1
        new_y_pos = self.gamemap.map_data['width']/5 * y_pos_multiplier
        
        print(f"{self.name} collided with {other.name}!")
        self.client.send_data({
            "new_physics": {
                "pos": [self.pos[0], new_y_pos],
                "vel": 0,
                "acc": 0,
                "angle": self.gamemap.angle_at(self.pos[0]),
                "hitbox_radius": self.hitbox_radius,
                "keys": self.key_presses
            }, 
            "crash_end_timestamp": end_timestamp
        }, 'crash')
        
    def on_wall_collide(self) -> None:
        """
        Called when this entity collides with world geometry (such as going too far off the track)
        """
        
        # new physics: set velocity to 0, set acceleration to 0, set angle to track angle, and set y_pos to 0
        
        self.client.send_data({
            "new_physics": {
                "pos": [self.pos[0], 0],
                "vel": 0,
                "acc": 0,
                "angle": self.gamemap.angle_at(self.pos[0]),
                "hitbox_radius": self.hitbox_radius,
                "keys": self.key_presses
            },
            "crash_end_timestamp": time_ns()/1e9 + CRASH_DURATION
        }, 'crash')
        
        

