from typing import Tuple, TYPE_CHECKING
from time import time_ns
import math

class Entity:
    """
    Represents a car. (for now, can generalize later).
    
    ### This must be the exact same as on the server side
    ^ just with a few server-related things removed, like client objects
    
    Has pos, vel, acc, angle, and a circular hitbox with a certain radius.
    
    Implements a few testing functions that randomize movement
    
    angle is just the dir in which they are facing right now, not the angle of any physics vector. Its mostly cosmetic.
    
    ### IMPORANT ANGLE INFO:
    0 is rightward (+x), 90 is upward (+y), 180 is leftward (-x), 270 is downward (-y)
    
    Thus, turning left would be increasing the angle, and turning right would be decreasing the angle.
    """
    def __init__(
        self,
        name: str,
        color: str,
        pos: Tuple[float, float],
        vel: Tuple[float, float] = (0, 0),
        acc: Tuple[float, float] = (0, 0),
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: list[bool] = [False, False, False, False]
        ) -> None:
        
        self.name = name
        self.color = color
        self.pos = list(pos)
        self.vel = list(vel)
        self.acc = list(acc)
        self.angle = angle
        self.hitbox_radius = hitbox_radius
        
        self.last_update_timestamp = time_ns()
    
        # False = key is not held down, True = key is held down
        # Use this to update acceleration and angle
        # w = +acc, s = -acc, a = +angle, d = -angle
        self.key_presses = keys
        """ `[forward, backward, left, right]` """
        
    def update(self):
        """
        Calculates the following:
            - `pos` based on `vel`
            - `vel` based on `acc`
            
            - `acc` based on `key_presses` and `angle`
            - `angle` based on `key_presses`
           
        Changes are scaled based on time elapsed since last update, which is stored in `GameManager`.
        
        This should be run as often as possible.
        """
        
        delta_time_s = (self.last_update_timestamp - time_ns()) / 1e9
        
        # for now, when left/right are held, we can turn 50 degrees per second
        # TODO ^ some sort of turning acceleration (since its a car)
        self.angle += (50*self.key_presses[2] - 50*self.key_presses[3]) * delta_time_s
        
        # use the angle to determine components of acceleration
        self.acc_mag = 2*self.key_presses[0] - 2*self.key_presses[1]
        self.acc[0] = self.acc_mag * math.cos(math.radians(self.angle))
        self.acc[1] = self.acc_mag * math.sin(math.radians(self.angle))

        # update velocity using acceleration
        self.vel[0] += self.acc[0] * delta_time_s
        self.vel[1] += self.acc[1] * delta_time_s
        
        # update position using velocity
        self.pos[0] += self.vel[0] * delta_time_s
        self.pos[1] += self.vel[1] * delta_time_s
        
        self.last_update_timestamp = time_ns()
    
    def get_physics_data(self) -> dict:
        """
        Return all physical data in a dict of the following format:
        
        ```python
        {
            "pos": [px, py],
            "vel": [vx, vy],
            "acc": [ax, ay],
            "angle": angle,
            "hitbox_radius": hitbox_radius,
        }
        ```
        """
        
        return {
            "pos": self.pos,
            "vel": self.vel,
            "acc": self.acc,
            "angle": self.angle,
            "hitbox_radius": self.hitbox_radius,
        }
    
    def set_physics(self, data: dict) -> None:
        """
        Set and override the current physics data. This should only be used with server data (or for testing)
        
        `data` must be a dict in the same format as the one returned by `get_physics_data()`, which looks like this:
        
        ```python
        {
            "pos": [px, py],
            "vel": [vx, vy],
            "acc": [ax, ay],
            "angle": angle,
            "hitbox_radius": hitbox_radius,
            "keys": [forward, backward, left, right]
        }
        ```
        
        Note: does NOT check for collisions after setting, however that should be handled on the next frame.
        """
        
        self.pos = data["pos"]
        self.vel = data["vel"]
        self.acc = data["acc"]
        self.angle = data["angle"]
        self.hitbox_radius = data["hitbox_radius"]
        self.key_presses = data["keys"]
        
        self.last_update_timestamp = time_ns()
    
    def on_entity_collide(self, other: 'Entity') -> None:
        """
        Called when this entity collides, but it must be WITH ANOTHER ENTITY.
        """
        
        print(f"{self.name} collided with {other.name}!")
        
    def on_wall_collide(self) -> None:
        """
        Called when this entity collides with world geometry (such as going too far off the track)
        """
        
        print(f"{self.name} collided with a wall!")