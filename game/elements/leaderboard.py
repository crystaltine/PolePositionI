import pygame
from typing import List, Dict

from managers import GameManager
from CONSTANTS import *

GOLD_COLOR = (255, 215, 0)
SILVER_COLOR = (192, 192, 192)
BRONZE_COLOR = (205, 127, 50)
REGULAR_COLOR = (60, 62, 64)

OPACITY = 200

class Leaderboard:
    """
    Handles logic with managing and displaying the leaderboard for the game over screen.
    
    The end result should look something like the following:
    ```
    +------------------------------------------+
    | 1. [car] firstplacegamer            100% |
    +------------------------------------------+
    +------------------------------------------+
    | 2. [car] some_username               79% |
    +------------------------------------------+
    +------------------------------------------+
    | 3. [car] bird                        57% |
    +------------------------------------------+
    ```
    """
    
    def __init__(self, sorted_players: List[Dict]):
        """
        @param `sorted_players` - should be the exact same as the data format received in `../screens/game_end.py` >> `game_end()`

        Example:
        ```python
        [
            {
                "username": "some_username",
                "color": "some_color,
                "score": "79%" 
            },
            ...
        ]
        ```
        """
        self.players = sorted_players
        
    @staticmethod
    def calculate_y_pos(index: int) -> int:
        """
        Calculates the y position of the given leaderboard index.
        
        Each entry will be 55 pixels tall, with 12 pixels of margin between each entry.
        """
        
        #      base y-value | height of each entry | margin between each entry
        return 127 +          index * 55 +             (index + 1) * 12
    
    def get_surface(index: int, username: str, car_color: str, score: str) -> pygame.Surface:
        """
        Returns a surface containing the formatted leaderboard entry.
        
        Should look something like this ascii art:
    
        ```
        +------------------------------------------+
        | 2. [car] some_username               79% |
        +------------------------------------------+
        ```
        """
        
        # each entry will be 45 pixels tall and 500 pixels wide
        
        entry = pygame.Surface((880, 55), pygame.SRCALPHA)
        
        color = (
            GOLD_COLOR if index == 0 
            else SILVER_COLOR if index == 1 
            else BRONZE_COLOR if index == 2 
            else REGULAR_COLOR
        )
        
        entry.fill((*color, OPACITY))
        
        # 5px vertical padding, 10px horizontal padding (see below)
        # IMPORTANT: font-medium final mounted height is actually 35px.
        
        car_texture = pygame.image.load(f'./game/assets/lobby/cars/car_{car_color}.png')
        # transform to a 45x45 image (10px taller than text, but because of internal padding it looks the same)
        car_texture = pygame.transform.scale(car_texture, (45, 45))
        
        
        placement_text = FONT_MEDIUM.render(f"{index + 1}.", True, (255, 255, 255))
        username_text = FONT_MEDIUM.render(username, True, (255, 255, 255))
        
        entry.blit(placement_text, (10, 10))
        entry.blit(car_texture, (45 + 20, 5))
        entry.blit(username_text, (45 + 20 + car_texture.get_width() + 10, 10))
        
        # things to blit right-jusitifed
        score_text = FONT_MEDIUM.render(score, True, (255, 255, 255))
        entry.blit(score_text, (entry.get_width() - score_text.get_width() - 10, 10))
        
        return entry
    
    def draw_leaderboard(self, elapsed: float) -> None:
        """
        Draws the leaderboard in order.
        
        Pass in elapsed time to animate opacity:
        At 3 seconds, opacity=0 -> 4 sec, opacity=1
        
        Linear animation
        """
        
        fadein_mult = elapsed - 3
        
        curr_y_pos = 127
        for i, player in enumerate(self.players):
            entry = Leaderboard.get_surface(i, player["username"], player["color"], player["score"])
            
            entry.set_alpha(255 * fadein_mult)
            
            GameManager.screen.blit(entry, (20, curr_y_pos))
            
            curr_y_pos += entry.get_height() + 12