import math
from typing import Tuple
from time import time_ns
from CONSTANTS import DRAG_MULTIPLIER

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
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 0,
        ) -> None:
        
        self.name = name
        self.color = color
        self.client = client
        self.pos = list(pos)
        self.vel = list(vel)
        self.acc = list(acc)
        self.angle = angle%360
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
        
        delta_time_s = (time_ns() - self.last_update_timestamp) / 1e9
        
        #total velocity
        total_vel = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)


        #Aidan change: making max turning 20 degrees a second and not allowing the user to turn if they are stopped
        #if statement to deal with corner case of not allowing user to turn while not moving, this is to stop users from going backwards
        if total_vel == 0:
            self.angle += 0
        else:
            #50 * True or False guarantees that turning has the correct behavior based on which keys are pressed down in any 
            #if none are pressed then it has an angle change of 0, if both then 0, only difference is when one is pressed and not the other
            denominator = 0.1 * total_vel+ 2.22 
            #value that changes how much a person can turn based on speed 
            angular_accel = 10/denominator + .5
            self.angle += (angular_accel*self.key_presses[3] - angular_accel*self.key_presses[2]) * delta_time_s
        #set angle back down 
        self.angle %= 360
        
        # use the angle to determine components of acceleration
        # READ: im getting rid of keypress=accel and just doing keypress=vel for now
        # self.acc_mag = 2*self.key_presses[0] - 2*self.key_presses[1]
        # self.acc[0] = self.acc_mag * math.cos(math.radians(self.angle%360))
        # self.acc[1] = self.acc_mag * math.sin(math.radians(self.angle%360))
        
        #add to total velocity with the acceleration and how long it was pressed for, maybe a change needed since the acceleration doesn't change 
        #until the next tick im pretty sure the conversion is based on just multiplying by the time for all but talk to michael
        total_vel += self.acc * delta_time_s

        self.vel[0] = total_vel * math.cos(math.radians(self.angle))
        self.vel[1] = total_vel * math.sin(math.radians(self.angle))
        
        # TODO - add some sort of drag/velocity loss when no acceleration
        
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
            "angle": self.angle%360,
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