import pygame
import time

from managers import GameManager, RenderingManager
from CONSTANTS import *
from elements.leaderboard import Leaderboard
from elements.button import Button

# Game Over! text setup
gameover_text = FONT_HUGE.render(f"GAME OVER!", True, (255, 255, 255))
container_dims = (gameover_text.get_width() + 20, gameover_text.get_height() + 20)

game_over_container = pygame.surface.Surface(container_dims, pygame.SRCALPHA)
game_over_container.fill((0, 0, 0, 128))

text_x = (container_dims[0] - gameover_text.get_width()) / 2
text_y = (container_dims[1] - gameover_text.get_height()) / 2
game_over_container.blit(gameover_text, (text_x, text_y))

def draw_gameover_text(seconds_since_screen_mounted: float) -> None:
    """
    This function draws the "Game Over!" text.
    
    Basically, when the screen first gets mounted, the text will be at the center of the screen and stay for about 2 seconds.
    After that, it will transition to the top left corner of the screen with a padding of 20px on either side.
    This transition should take about 1 second. After that it will stay there.
    
    ### Note for leaderboard UI:
    After the animation, the first leaderboard element should start at y=127.
    (this factors in a margin-bottom of 20px for the game over text container)
    """
    
    init_x = GameManager.screen.get_width()/2 - game_over_container.get_width()/2
    init_y = GameManager.screen.get_height()/2 - game_over_container.get_height()/2
    end_x = 20
    end_y = 20
    
    if seconds_since_screen_mounted < 2:
        # draw in the center
        GameManager.screen.blit(game_over_container, (init_x, init_y))
    elif seconds_since_screen_mounted < 3:
        x_pos = init_x + (end_x - init_x) * (seconds_since_screen_mounted - 2)**0.5 # ease out
        y_pos = init_y + (end_y - init_y) * (seconds_since_screen_mounted - 2)**0.5 # ease out
        
        GameManager.screen.blit(game_over_container, (x_pos, y_pos))
        
    else:
        GameManager.screen.blit(game_over_container, (end_x, end_y))

def draw_ending_sidebar(seconds_since_screen_mounted: float) -> None:
    """
    Draws the sidebar on the right side of the game end screen.
    
    Animation:
    
    At 4 seconds, opacity=0 -> 5 sec, opacity=1
    """
    side_panel = pygame.surface.Surface((280,720), pygame.SRCALPHA)
    side_panel.fill((0, 0, 0, 128))
    
    # Load the 240x240 map preview
    map_preview = pygame.image.load(f'./game/assets/lobby/maps/{GameManager.map_data["preview_file"]}')
    side_panel.blit(map_preview, (20, 20))
    
    map_label = FONT_TINY.render("Map:", True, (255, 255, 255))
    map_text = FONT_MEDIUM.render(GameManager.map_data['map_name'], True, (255, 255, 255))
    length_label = FONT_TINY.render("Track length:", True, (255, 255, 255))
    length_text = FONT_MEDIUM.render(f"{GameManager.map_data['length']} m", True, (255, 255, 255))
    record_label = FONT_TINY.render("WR time:", True, (255, 255, 255))
    record_text = FONT_MEDIUM.render(f"{GameManager.map_data['wr_time']} s", True, (255, 255, 255))
    
    LABEL_GAP = 5
    DESC_GAP = 20
    
    side_panel.blit(map_label, (20, 280))
    side_panel.blit(map_text, (20, 280 + FONT_SIZES["tiny"] + LABEL_GAP)) # gap of 5px between label and value
    
    side_panel.blit(length_label, (20, 280 + FONT_SIZES["tiny"] + LABEL_GAP + FONT_SIZES["medium"] + DESC_GAP)) # gap of 10px between text objects
    side_panel.blit(length_text, (20, 280 + 2*FONT_SIZES["tiny"] + 2*LABEL_GAP + FONT_SIZES["medium"] + DESC_GAP))
    
    side_panel.blit(record_label, (20, 280 + 2*FONT_SIZES["tiny"] + 2*LABEL_GAP + 2*FONT_SIZES["medium"] + 2*DESC_GAP))
    side_panel.blit(record_text, (20, 280 + 3*FONT_SIZES["tiny"] + 3*LABEL_GAP + 2*FONT_SIZES["medium"] + 2*DESC_GAP))
    
    #side_panel.blit(pb_label, (20, 280 + 3*FONT_SIZES["tiny"] + 3*LABEL_GAP + 3*FONT_SIZES["medium"] + 3*DESC_GAP))
    #side_panel.blit(pb_text, (20, 280 + 4*FONT_SIZES["tiny"] + 4*LABEL_GAP + 3*FONT_SIZES["medium"] + 3*DESC_GAP))
    
    # There is a 20px "padding" in side_panel because these buttons are 240px but the panel is 280px
    
    side_panel.set_alpha(255 * (seconds_since_screen_mounted - 4))
    
    GameManager.screen.blit(side_panel, (920, 0))

def game_end(leaderboard_data: list) -> None:
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
            "score": "79%" 
        },
        ...
    ]
    ```
    
    Upon return, go back to the main menu.
    """

    leaderboard = Leaderboard(leaderboard_data)
    
    start_timestamp = time.time()
    
    exit_button = Button((940,640), "Exit", "#ffffff", "#ff9696", BUTTON_MEDIUM)
    while True:
        
        elapsed = time.time() - start_timestamp
        
        GameManager.draw_static_background()
        
        draw_gameover_text(elapsed)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameManager.quit_game()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.is_hovering(pygame.mouse.get_pos()):
                    # leave the room
                    GameManager.http_man.leave_room()
                    return
                
        if elapsed > 3:
            leaderboard.draw_leaderboard(elapsed)
            if elapsed > 4:
                draw_ending_sidebar(elapsed)
                
                exit_button.changeColor(pygame.mouse.get_pos())
                exit_button.update(GameManager.screen)
        
        
                
        pygame.display.update()