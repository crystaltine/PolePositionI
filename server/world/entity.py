import math
from typing import Tuple
from time import time_ns

class Entity:
    """
    Represents a car. (for now, can generalize later).
    Has pos, vel, acc, angle, and a circular hitbox with a certain radius.
    
    ### This must effectively be the same as on the client side
    ^ just with a few extra things maybe, since we have to deal with client objects
    
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
        client,
        pos: Tuple[float, float],
        vel: Tuple[float, float] = (0, 0),
        acc: Tuple[float, float] = (0, 0),
        angle: float = 0,
        hitbox_radius: float = 0,
        ) -> None:
        
        self.name = name
        self.color = color
        self.client = client
        self.pos = list(pos)
        self.vel = list(vel)
        self.acc = list(acc)
        self.angle = angle
        self.hitbox_radius = hitbox_radius
        
        self.last_update_timestamp = time_ns()
        
        # False = key is not held down, True = key is held down
        # Use this to update acceleration and angle
        # w = +acc, s = -acc, a = +angle, d = -angle
        self.key_presses = [False, False, False, False]
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
        Calculates the following:
            - `pos` based on `vel`
            - `vel` based on `acc`
            
            - `acc` based on `key_presses` and `angle`
            - `angle` based on `key_presses`
            
        Should be run on every server tick (for now, 24tps) - see `../CONSTANTS.py`
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
            "keys": [forward, backward, left, right]
        }
        ```
        """
        
        return {
            "pos": self.pos,
            "vel": self.vel,
            "acc": self.acc,
            "angle": self.angle,
            "hitbox_radius": self.hitbox_radius,
            "keys": self.key_presses
        }
        
    def on_entity_collide(self, other: 'Entity') -> None:
        """
        Called when this entity collides, but it must be WITH ANOTHER ENTITY.
        """
        
        print(f"{self.name} collided with {other.name}!")
        self.client.send_data({}, 'crash')
        
    def on_wall_collide(self) -> None:
        """
        Called when this entity collides with world geometry (such as going too far off the track)
        """
        
        print(f"{self.name} collided with a wall!")
        self.client.send_data({}, 'crash')