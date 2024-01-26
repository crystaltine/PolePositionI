from CONSTANTS import MAPS
import random

class GameMap:
    """
    Represents a racetrack object and its information, such as length and world record time.
    """
    
    def __init__(self, map_name: str = None):
        """
        Creates a new GameMap object. If no map name is provided, a random map is picked.
        """
        
        if map_name is None: map_name = random.choice(list(MAPS.keys()))
        
        elif not map_name in MAPS.keys():
            raise ValueError(f"Map name {map_name} not found in maps list!")
        
        self.map_name = map_name
        self.map_data = MAPS[map_name] # {length: string, wr_time: number}