from typing import Dict, List

from world.entity import Entity
from game_map import GameMap

class World:
    """
    A container for all Entity objects loaded into a game.
    
    Must be initialized with a specific map.
    """
        
    def __init__(self, map_details: dict):
        """
        Creates a new World object with the specified map details, 
        which should be obtained from the server on room creation/join.
        
        Because this is client side, it does not check for collisions.
        """
        self.gamemap = GameMap(map_details)
        self.entities: Dict[str, Entity] = {}
        """ a map from username to entity objects """
        
    def create_entity(
        self, 
        name: str,
        color: str,
        pos: List[float], 
        vel: float = 0,
        acc: float = 0,
        angle: float = 0,
        hitbox_radius: float = 0,
        keys: list[bool] = [False, False, False, False]
        ) -> Entity:
        """
        Creates and places an entity at a certain position. 
        Optionally can supply initial velocity, acceleration, angle, and hitbox radius.
        
        Returns a reference the entity.
        """
        
        e = Entity(name, color, self.gamemap, pos, vel, acc, angle, hitbox_radius, keys)
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
          width: number,
          oob_leniency: number,
          length: number,
          wr_time: number,
        } 
        ```
        """
        return self.gamemap.map_data
       