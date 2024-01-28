import pygame
import math
from typing import Union

from game_manager import GameManager
from map_utils import get_map
from world.world import World
from world.entity import Entity
from CONSTANTS import WIDTH, HEIGHT, FOV

class GameRenderer:
    """
    Handles all rendering of the live game, as well as all updates to the internal physics engine
    based on the data the server sends us (every minute)
    
    We keep an internal physics engine for smoother animations, although server data overrides this.
    
    @TODO - we should probably destroy this object when the game ends (once we implement game end logic)
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
        """
        Draws on the screen a single frame based on the current state of the internal physics engine.
        """
        
        GameManager.draw_dynamic_background(GameManager.get_our_entity().angle)
        GameManager.draw_car()
        
        # For each other entity, draw on screen
        for other in GameManager.get_all_other_entities():
            size = GameRenderer.get_rendered_size(other)
            pos = (WIDTH/2 + GameRenderer.angle_offset(other), GameRenderer.get_y_pos(other))
            GameManager.draw_entity(size, pos, other.color)

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
        
        # update world
        self.tick_world()
     
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
            
    @staticmethod
    def get_rendered_size(other: Entity) -> int:
        """
        ### See `../RENDERER_NOTES.png`
        
        Returns a size in px for the eneity based on how far away and at what angle it is from us.
        """
        
        us = GameManager.get_our_entity()
        
        dist = math.sqrt((other.pos[0] - us.pos[0])**2 + (other.pos[1] - us.pos[1])**2)
        theta = math.asin(other.hitbox_radius / (dist + other.hitbox_radius))
        width_on_screen = (WIDTH/2) * 4*theta/math.pi # 2 and 4 are static (do not adjust)
        
        return round(width_on_screen)
        
    @staticmethod
    def get_y_pos(other: Entity) -> int:
        """
        Returns a y-position on the screen based on an entity's distance from us.
        
        The idea is that farther away entities should be drawn higher up (lower y-value)
        because they are closer to the horizon.
        
        Will not return a value lower than 300 (the horizon)
        and higher than 600 (bottom of screen, with some padding ofc)
        
        ### The function used for this calculation
        (can be changed - i just picked a random asymptotic decay from 600->300 in desmos)
        
        y_coord = `30000/(dist+100) + 300`
        """    
        
        us = GameManager.get_our_entity()
        
        dist = math.sqrt((other.pos[0] - us.pos[0])**2 + (other.pos[1] - us.pos[1])**2)
        return round(30000/(dist+100) + 300)
        
    @staticmethod
    def angle_offset(other: Entity) -> Union[int, None]:
        """
        ### See `../RENDERER_NOTES.png`
        
        Returns how many pixels relative to the center of the screen we should draw CENTER of the other entity at,
        based on the angle between us and the other entity.
        
        If they are off screen (angle > FOV/2), returns None. In this case, don't draw on screen.
        """
        
        us = GameManager.get_our_entity()
        
        theta = math.atan2(other.pos[1] - us.pos[1], other.pos[0] - us.pos[0])
        D = 8*theta/math.pi * (WIDTH/2)
        
        return -D # the math makes pos=left, so we have to negate to match screen coords
    
    @staticmethod
    def draw_entity(size: int, pos: tuple[int, int], color: str) -> None:
        """
        Draws an entity on the screen, given a size, offset, and color.
        
        Currently, all it draws is a circle. (TODO - implement 3d models/rotating sprites)
        """
        
        pygame.draw.circle(GameManager.screen, color, pos, size)