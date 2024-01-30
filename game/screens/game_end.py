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





    #uncomment once able to run in real game
    #RenderingManager.render_frame()
    

    while True:
        # draw the countdown
        text = FONT_LARGE.render(f"GAME OVER", True, (255, 255, 255))
        
        container_dims = (text.get_width() + 20, text.get_height() + 20)
        countdown_container = pygame.surface.Surface(container_dims, pygame.SRCALPHA)
        countdown_container.fill((0, 0, 0, 128))
        
        text_x = (container_dims[0] - text.get_width()) / 2
        text_y = (container_dims[1] - text.get_height()) / 2
        countdown_container.blit(text, (text_x, text_y))
        
        # blit onto the screen
        GameManager.screen.blit(countdown_container, (GameManager.screen.get_width()/2 - container_dims[0]/2, GameManager.screen.get_height()/2 - container_dims[1]/2))
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit_game()
                
        pygame.display.update()