import pygame
from CONSTANTS import FONT_SMALL

def waiting_lobby_player(username: str, car_color: str, is_leader = False) -> pygame.surface.Surface:
    """
    Creates a component that represents a player when on the waiting lobby screen (`./screens/waiting_room.py`)
    
    Returns a `pygame.surface.Surface` component that can be mounted on any other element.
    """
    
    base_component = pygame.image.load('./game/assets/waiting_room_player_component.png')
    pygame.transform.scale(base_component, (200, 200))
    
    username_text = FONT_SMALL.render(username, True, '#000000')
    base_component.blit(username_text, (100-username_text.get_width()//2, 170-username_text.get_height()//2))
    
    return base_component