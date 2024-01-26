import pygame
from CONSTANTS import FONT_SMALL

def waiting_lobby_player(username: str, car_color: str, is_leader = False) -> pygame.surface.Surface:
    """
    Creates a component that represents a player when on the waiting lobby screen (`./screens/waiting_room.py`)
    
    ### Important: 
    `car_color` must be one of the following:
    + `'blue'`
    + `'green'`
    + `'orange'`
    + `'pink'`
    + `'purple'`
    + `'red'`
    + `'yellow'`
    + `'white'`
    
    Using `is_leader = True` will render a crown on top of the player's car. (to show that they are the host of the room)
    
    Returns a `pygame.surface.Surface` component that can be mounted on any other element.
    """
    
    base_component = pygame.image.load('./game/assets/waiting_room_player_component.png')
    pygame.transform.scale(base_component, (200, 200))
    
    username_text = FONT_SMALL.render(username, True, '#000000')
    base_component.blit(username_text, (100-username_text.get_width()//2, 170-username_text.get_height()//2))
    
    # Now we render a car image on top of the pedestal image.
    # The actual opaque part of this pedestal is the bottom ~100 px of the 200px image, so
    # the car should be about 80px tall (to leave a bit of padding) and be mounted at height 10px
    car_texture = pygame.image.load(f'./game/assets/lobby/cars/car_{car_color}.png')
    base_component.blit(car_texture, (100-car_texture.get_width()//2, 10))
    
    if is_leader:
        crown_texture = pygame.image.load('./game/assets/lobby/leader_crown.png')
        pygame.transform.scale(crown_texture, (40, 40))
        base_component.blit(crown_texture, (30, 10)) # so that it looks like it's on top of the car
    
    return base_component