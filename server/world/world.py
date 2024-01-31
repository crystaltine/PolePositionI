from typing import Dict, List
from time import time_ns
import math

from world.entity import Entity
from game_map import GameMap

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
    A container for all Entity objects loaded into a game.
    
    Must be initialized with a specific map.
    """
        
    def __init__(self, map_name: str = None) -> None:
        """
        Creates a new World object with no entities added.
        
        If no map name is provided, a random map is picked.
        """
        self.gamemap = GameMap(map_name)
        self.entities: Dict[str, Entity] = {}
        """ a map from client_ids to entity objects """
        
    def create_entity(
        self, 
        name: str,
        color: str,
        client,
        pos: List[float], 
        vel: float = 0,
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 2.5
        ) -> Entity:
        """
        Creates and places an entity at a certain position. 
        Optionally can supply initial velocity, acceleration, angle, and hitbox radius.
        
        Returns a reference the entity.
        """
        
        e = Entity(name, color, client, self.gamemap, pos, vel, acc, angle, hitbox_radius)
        self.entities[client.id] = e
        
        return e
        
    def destroy_entity(self, client_id: str) -> None:
        """
        Removes the entity with the specified client_id from the world.
        """
        
        del self.entities[client_id]
        
    def update(self) -> bool:
        """
        Updates all entities in the world.
        
        This also handles all collisions.
        
        Each Entity object will automatically handle any out-of-bounds crashing,
        and this function automatically handles any entity-entity collisions.
        
        Returns `True` if the game has ended, `False` otherwise.
        """
        
        [e.update() for e in self.entities.values()]   
        
        # check for win before collisions because if you cross then game technically ends
        win_result = self.check_win()
        
        if not win_result:
            # check for collisions   
            self.check_entity_collisions()
        
        return win_result
    
    def check_win(self) -> bool:
        """
        Checks the progress of all entities in the world.
        
        If one of them has reached the end of the map, 
        send the game-end event to all clients, along with the leaderboard
        
        Returns `True` if the game has ended, `False` otherwise.
        """  
        
        progresses = [e.get_progress() for e in self.entities.values()]
        
        if any([p >= 1 for p in progresses]):

            sorted_results = sorted(
                [{
                    "username": e.name,
                    "color": e.color,
                    "score": f"{round(p*100)}%",
                    "raw_score": p,
                } for e, p in zip(self.entities.values(), progresses)],
                key=lambda x: x["raw_score"],
                reverse=True # highest progress first
            )
            
            for entity in self.entities.values():
                entity.client.send_data(sorted_results, "game-end")
                entity.client.stop_receiving = True
            
            return True
        else: 
            return False
        
    def check_entity_collisions(self) -> None:
        """
        Checks for collisions between entities.
        
        Since there are only 8 players max, a brute force approach should be fine.
        (we would only check 28 pairs max)
        """
        entity_list = list(self.entities.values())
        
        # pick two entites, check if they are colliding
        for i in range(len(entity_list)):            
            for j in range(i+1, len(entity_list)):
                
                if are_colliding(e1:=entity_list[i], e2:=entity_list[j]):
                    # Tell both entities that they crashed
                    crash_end_timestamp = time_ns()/1e9 + CRASH_DURATION
                    e1.on_entity_collide(e2, 'left', crash_end_timestamp)
                    e2.on_entity_collide(e1, 'right', crash_end_timestamp)

    def out_of_bounds(self) -> None:
        """
        Checks if the entities have gone too far off the track 
        
        All entities that have gone too far will be crashed and the info will be sent to client
        """
        entity_list = list(self.entities.values())

        for entity in entity_list:
            #with new physics center of track is always going to be 0
            #x pos is just how far along the track you are and y val is your y pos 
            #just checks to see how far you deviate from 0 and if too far then crash
            dist = entity.pos[1]
            #track is 200 m wide and 0 is the center of it, this gives 30 m of leniency which might be too much of how far off you can go
            if dist > 130:
                entity.on_wall_collide()
                    
    def get_world_data(self) -> list:
        """
        Returns a JSON-serializable list of dicts containing all data for every entity in the world.
        
        Schema:
        ```typescript
        [
          {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: number,
              acc: number,
              angle: number, // in degrees
              hitbox_radius: number,
              keys: [forward: bool, backward: bool, left: bool, right: bool]
            }
          },
          ...
        ]
        ```
        """
       
        return [{
            "username": e.name,
            "color": e.color,
            "physics": e.get_physics_data()
        } for e in self.entities.values()]
        
    def get_map_data(self) -> dict:
        """
        Returns data about the loaded map on this world.
        
        This data is of the schema:
        ```typescript
        {
          map_name: string,
          map_file: string, // the file inside ./maps, on both the server and client
          preview_file: string, // the file the client should load as a waiting room preview img
          length: number,
          wr_time: number,
        } 
        ```
        """
        return self.gamemap.map_data