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
        #Tuples are for x and y values of 
        pos: Tuple[float, float],
        vel: Tuple[float, float] = (0, 0),
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: list[bool] = [False, False, False, False]
        ) -> None:
        
        #instance variables 
        self.name = name
        self.color = color
        self.pos = list(pos)
        self.vel = list(vel)
        #might cause issues, michael originally had acc as a list but i'm changing that here 
        self.acc = acc
        self.angle = angle%360
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
        #convert nanosecond difference to seconds
        delta_time_s = (time_ns() - self.last_update_timestamp) / 1e9
        


        #total velocity
        total_vel = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)

        # update acceleration, required for calculations below
        #if statement used to see if only braking is pressed
        if self.key_presses[1] and not self.key_presses[0]:
            self.acc = -10
        else:
            #when multiplying by a boolean True acts as a 1 and False acts as 0
            #these references to self.key_presses are to deal with forward and backwards being pressed 
            #at the same time, or none. It ensures correct behavior based on the keys that are being pressed
            #this also deals with drag as the drag increases as speed does and will set the acceleration when both keys or neither is pressed
            #it also incorporates speed into our acceleration
            self.acc = math.sqrt(100*self.key_presses[0] - 100*self.key_presses[1]) - math.sqrt(total_vel)



        #if statement to deal with corner case of not allowing user to turn while not moving, this is to stop users from going backwards
        if total_vel == 0:
            self.angle += 0
        else:
            #calculations to simulate how much you can turn based on your speed
            #faster = slower turning and vice versa for slower speed
            denominator = 0.1 * total_vel+ 2.22 
            angular_accel = 10/denominator + .5

            #same logic above with the acceleration, self.key_presses[2] increases angle and self.key_presses[3] decreases
            #done to handle multiple keys pressed at once 
            #50 * True or False guarantees that turning has the correct behavior based on which keys are pressed down in any 
            self.angle += (angular_accel*self.key_presses[2] - angular_accel*self.key_presses[3]) * delta_time_s
        
        #since angle is constantly being added to, % will reset the angle back down to in range of 0-360 degrees so trig calculations are correct
        self.angle %= 360

        #add to total velocity with the acceleration and how long it was pressed for, maybe a change needed since the acceleration doesn't change 
        #until the next tick im pretty sure the conversion is based on just multiplying by the time for all but talk to michael
        #max function used to ensure that players are unable to reverse 
        total_vel = max(0, min(total_vel + self.acc * delta_time_s, 100))

        self.vel[0] = total_vel * math.cos(math.radians(self.angle))
        self.vel[1] = total_vel * math.sin(math.radians(self.angle))
        
        
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
        self.angle = data["angle"]%360
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