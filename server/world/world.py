from typing import Dict
from world.entity import Entity
import math

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
    
    Basically, stores players as circular objects, each with their own pos, vel, acc.

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
        """ a map from client_ids to entity objects """
        
    def create_entity(
        self, 
        name: str,
        color: str,
        client,
        pos: tuple[float, float], 
        vel: tuple[float, float] = (0, 0), 
        acc: tuple[float, float] = (0, 0),
        angle: float = 0,
        hitbox_radius: float = 2.5
        ) -> Entity:
        """
        Creates and places an entity at a certain position. 
        Optionally can supply initial velocity, acceleration, angle, and hitbox radius.
        
        However, it is recommended to give it a hitbox radius, as the default is no hitbox.
        
        Returns the entity.
        """
        
        e = Entity(name, color, client, pos, vel, acc, angle, hitbox_radius)
        self.entities[client.id] = e
        
        return e
        
    def destroy_entity(self, client_id: str) -> None:
        """
        Removes the entity with the specified client_id from the world.
        """
        
        del self.entities[client_id]
        
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
                "username": e.name,
                "color": e.color,
                "physics": e.get_physics_data()
            })
        
        return data