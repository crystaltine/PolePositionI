import pygame
import time

from managers import GameManager, RenderingManager
from CONSTANTS import FONT_LARGE, FONT_SIZES

def countdown():
    """
    Renders the world, then begins a countdown overlaying it
    until the timestamp in `GameManager.start_timestamp` is reached.
    """

    while True:
        
        time_left = int(GameManager.start_timestamp - time.time())
        
        if time.time() >= GameManager.start_timestamp:
            # After we return out of this, `../main.py` will call `live_game``
            return

        RenderingManager.render_frame()
        
        # draw the countdown
        text = FONT_LARGE.render(f"{time_left if time_left>0 else 'Go!'}", True, (255, 255, 255))
        
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