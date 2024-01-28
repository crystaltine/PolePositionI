import random
from typing import Tuple
import math


class Entity:
    """
    Currently a temp, proof-of-concept object for use in the `World` class. 
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
        client,
        pos: Tuple[float, float],
        vel: Tuple[float, float] = (0, 0),
        acc: Tuple[float, float] = (0, 0),
        angle: float = 0,
        hitbox_radius: float = 0,
        ) -> None:
        
        self.name = name
        self.client = client
        self.pos = list(pos)
        self.vel = list(vel)
        self.acc = list(acc)
        self.angle = angle
        self.hitbox_radius = hitbox_radius
        
        # False = key is not held down, True = key is held down
        # Use this to update acceleration and angle
        # w = +acc, s = -acc, a = +angle, d = -angle
        # TODO: im just going to use some abritrary acc and angle change values for now
        self.key_presses = [False, False, False, False]
        """ `[forward, backward, left, right]` - see `./key_decoder.py` for more info."""
        
    def set_random_angle(self) -> None:
        self.angle = random.randint(0, 360)
        
    def set_random_acceleration(self) -> None:
        self.acc = [random.randint(-2, 2), random.randint(-2, 2)]
    
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
        
        # for now, when left/right are pressed, we increase angle by 2 degrees
        # TODO ^ some sort of turning acceleration (since its a car)
        self.angle += 2*self.key_presses[2] - 2*self.key_presses[3]
        
        # use the angle to determine components of acceleration
        self.acc_mag = 2*self.key_presses[0] - 2*self.key_presses[1]
        self.acc[0] = self.acc_mag * math.cos(math.radians(self.angle))
        self.acc[1] = self.acc_mag * math.sin(math.radians(self.angle))
        
        # update velocity using acceleration
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]
        
        # update position using velocity
        self.pos[0] + self.vel[0]
        self.pos[1] + self.vel[1]
        
    def get_physics_data(self) -> list:
        """
        Return all physical data in a 7-element list
        Format: `[pos_x, pos_y, vel_x, vel_y, acc_x, acc_y, angle]`
        """
        
        return [
            self.pos[0], self.pos[1],
            self.vel[0], self.vel[1],
            self.acc[0], self.acc[1],
            self.angle
        ]
        
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