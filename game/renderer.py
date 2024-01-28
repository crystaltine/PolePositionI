import pygame
import sys

from game_manager import GameManager
from map_utils import get_map
from world.world import World

class GameRenderer:
    """
    Handles all rendering of the live game, as well as all updates to the internal physics engine
    based on the data the server sends us (every minute)
    
    We keep an internal physics engine for smoother animations, although server data overrides this.
    """
    
    def __init__(self, init_entities: list = []) -> None:
        """
        Creates a `GameRenderer` to run internal physics.
        
        Map name comes from `GameManager`.
        
        `init_entities` should be an (optional) list of entities, each of which is a dict of the format:
        ```typescript
        {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number
            }
        }
        """
        
        map_class = get_map(GameManager.map_name)
        self.world = World(map_class.world_size, map_class.track_geometry)
        
        for entity in init_entities:
            self.place_entity(entity)

    def render_frame():
        
        # TODO - place entities on the screen
        
        GameManager.draw_static_background()
        GameManager.draw_car()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.socket_man.socket.close()
                pygame.quit()
                sys.exit()

        pygame.display.update()
        
    def tick_world(self):
        """
        Updates the internal physics engine by one tick
        
        This depends on the FPS of the client-side game. 24/s at the time of writing
        """
        
        self.world.update()
    
    def place_entity(self, entity_data: dict) -> bool:
        """
        `entity_data` must be of the format:
        ```typescript
        {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number
            }
        }
        ```
        
        Adds the entity to the world.
        This should be used on the first physics data packet (or some special init packet once a game starts)
        
        Returns `True` if the entity is new (checked based on username) and was added, `False` if it already exists
        """
        
        if entity_data['username'] in self.world.entities:
            return False
        
        self.world.create_entity(
            entity_data['username'],
            entity_data['color'],
            **entity_data['physics']
        )
     
    def set_physics(self, data: list):
        """
        Updates the internal physics engine with the data the server sends us.
        
        This depends on the broadcast frequency of the server. 1/s at the time of writing
        
        `data` should have the same schema as the `World.get_all_data` function, which looks like this:
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
              hitbox_radius: number
            }
          },
          ...
        ]
        ```
        
        (each one of those objects is an entity)
        """
        
        # for each object in that list, update the corresponding entity.
        for entity_data in data:
            self.world.entities[entity_data['username']].set_physics(entity_data['physics'])