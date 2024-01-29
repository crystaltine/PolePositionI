import pygame
import time

from managers import GameManager, RenderingManager
from CONSTANTS import FONT_LARGE, FONT_SIZES

def game_end(leaderboard_data: list):
    """
    Renders one frame of the live game for background.
    
    Overlays "Game Over!" on top, and displays leaderboard after a short delay/animation.
    
    Call this after receiving the `game_end` event from the server.
    That event should also contain the SORTED leaderboard data, of the format:
    ```python
    [
        {
            "username": "some_username",
            "color": "some_color,
            "score/distance": "100%/3500m" 
        },
        ...
    ]
    ```
    """

    # TODO
    print("hi, lb data below:")
    for item in leaderboard_data:
        print(item)

    while True:
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit_game()
                
        pygame.display.update()