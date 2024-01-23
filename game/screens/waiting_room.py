import pygame
import sys; sys.path.append("C:\\Users\\s-msheng\\cs\\asp_3\\game")

from game_manager import GameManager

def waiting_room():
    """
    Creates/Mounts the room where the user is sent after creating/joining a room
    """
    while True:
        GameManager.draw_static_background()
        
        pygame.draw.rect(GameManager.screen, pygame.color.Color(0, 0, 0, 140), (800,0,400,720))   

waiting_room()