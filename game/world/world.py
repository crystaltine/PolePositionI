from typing import Dict
from world.entity import Entity
import math
import center_tracking

def are_colliding(e1: Entity, e2: Entity) -> bool:
    """
    Runs distance formula on two entities' positions.
    Returns whether or not the distance is less than the sum of their hitbox radii
    
    `True` if they are colliding, `False` otherwise. 
    """
    
    return math.sqrt(
        (e1.pos[0] - e2.pos[0])**2 + 
        (e1.pos[1] - e2.pos[1])**2
    ) < e1.hitbox_radius + e2.hitbox_radius

class World:
    """
    A 2D Plane that holds different `Entity` objects.
    
    Basically, stores players as circles, each with their own pos, vel, acc.

    To handle car collisions - send 'crash' event on the following: (UPDATE AFTER IMPLEMENTING HITBOXES)
        - if two players are within 5m of each other # TEMP - change to 2*hitbox_radius
        - within 2.5m of a wall/track boundary # TEMP - change to hitbox_radius
        - out of bounds (within 2.5m of the world boundaries) # TEMP - change to hitbox_radius
        - etc...
    
    Notes: 
        - We could do circular hitboxes to make collision detection much simpler and more efficient (just determine distance between points instead of having to factor in rotation and stuff)
        - We can also handle the camera relatively easily - on the client side, just do some scaling and other math to place enemy players correctly on the screen.
        - For example: if a player is rotated 0deg and an enemy is 400m away at 24deg, we could have a DISTANCE_SCALE function and a FOV function that calculates how small to make the player and how far off to the side to place the player on the screen.
        - Plus, doing this allows us to store tracks/maps pretty easily - just as a collection of points/shapes that define the track, and maybe a defining a certain radius around the track as the "track area" that players can't leave (or else they crash and respawn at the last checkpoint or something)
        """
        
    def __init__(self, size: tuple[int, int], track_geometry=None) -> None:
        """
        Creates a new World object with no entities added.
        
        ### Coordinate System:
        - `(0, 0)` is the bottom left corner (like the first quadrant of a graph)
        - `x` increases to the right
        - `y` increases upwards
        
        @TODO - in the future, the geometry params should be supplied by a map template, and should provide
        complete information about the track and obstacles.
        """
        self.size = size
        self.entities: Dict[str, Entity] = {}
        """ a map from username to entity objects """
        
    def create_entity(
        self, 
        name: str,
        color: str,
        pos: tuple[float, float], 
        vel: tuple[float, float] = (0, 0), 
        acc: tuple[float, float] = (0, 0),
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: list[bool] = [False, False, False, False]
        ) -> Entity:
        """
        Creates and places an entity at a certain position. 
        Optionally can supply initial velocity, acceleration, angle, and hitbox radius.
        
        However, it is recommended to give it a hitbox radius, as the default is no hitbox.
        
        Returns the entity.
        """
        
        e = Entity(name, color, pos, vel, acc, angle, hitbox_radius, keys)
        self.entities[name] = e
        
    def destroy_entity(self, name: str) -> None:
        """
        Removes the entity with the specified name from the world.
        """
        
        del self.entities[name]
        
    def update(self) -> None:
        """
        Updates all entities in the world.
        """
        for e in self.entities.values(): 
            e.update()
        
    def check_entity_collisions(self) -> None:
        """
        Checks for collisions between entities.
        If any two entities
        
        Since there are only 8 players max, a brute force approach should be fine.
        (we would only check 28 pairs max)
        """
        entity_list = list(self.entities.values())
        
        for i in range(len(entity_list)):
            
            # Check if they are colliding with a wall.
            # TODO ^ (we need to define the track geometry first)
            # for now, just use world coords
            
            e1 = entity_list[i]
            if (
                e1.pos[0] < e1.hitbox_radius or # off left side
                e1.pos[1] < e1.hitbox_radius or # off bottom side
                e1.pos[0] > self.size[0] - e1.hitbox_radius or # off right side
                e1.pos[1] > self.size[1] - e1.hitbox_radius # off top side
            ): 
                e1.on_wall_collide()
            
            for j in range(i+1, len(entity_list)):
                if are_colliding(e1, e2:=entity_list[j]):
                    
                    # Tell both entities that they crashed
                    e1.on_entity_collide(e2)
                    e2.on_entity_collide(e1)

    #TODO populate the center distances
    #out of bounds tracking that uses populate_center_distances when it is working               
    #integration of method from center_tracking.py
    #loops through all of the players and checks to see if they have gone to far from track
    #if they have then crash is sent to server
    def out_of_bounds (self):
        #create list of centers and list of cars
        centers = center_tracking.populate_center_distances()
        entity_list = list(self.entities.values())
        for i in range (len(entity_list)):
            #reset the distances, update which entity is being accounted for, and if car should be crashed
            distances = []
            entity = entity_list[i]
            #assume car is crashed unless one of the distances is close enough
            crashed = True
            #TODO replace values in range calcs with actual track values and adjust range if needed

            #getting range of x values around the entity to check distance to center 
            #max and min ensures that it doesn't go out of bounds, 5 is a range that can be increased or decreased if too lenient
            #0 and 1000 are placeholders for what would be the x beginning and end coords of track
            lower_x = max(0, entity.pos[0] - 5)
            upper_x = min(1000, entity.pos[0] + 5)
            #get distances from center for all values in range
            for i in range (upper_x - lower_x + 1):
                center_x = lower_x + i
                center_y = centers[center_x]
                distances.append(center_tracking.distance(entity.pos[0], entity.pos[1], center_x, center_y))
            for x in distances:
                if x < 30:
                    crashed = False
                    break
            if crashed:
                entity.on_wall_collide()
            

        
        
            
    def get_all_data(self) -> list:
        """
        Returns a JSON-serializable list of dicts containing all data about the world.
        
        Schema:
        ```typescript
        [
          {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number,
              keys: [forward: bool, backward: bool, left: bool, right: bool]
            }
          },
          ...
        ]
        ```
        """
        
        data = []
        
        for e in self.entities.values():
            data.append({
                "username": e.client.username,
                "color": e.color,
                "physics": e.get_physics_data()
            })
        
        return data