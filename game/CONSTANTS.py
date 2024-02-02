import pygame
import math

pygame.init()

id_map = {
    pygame.K_w: 0,
    pygame.K_UP: 0,
    pygame.K_s: 1,
    pygame.K_DOWN: 1,
    pygame.K_a: 2,
    pygame.K_LEFT: 2,
    pygame.K_d: 3,
    pygame.K_RIGHT: 3
}

WIDTH = 1200
HEIGHT = 720

FOV_DEGREES = 90
FOV = math.radians(FOV_DEGREES)
""" degrees in total (FOV/2 degrees visible on each side) """

ANGLE_ACCUMULATION_FACTOR = 1.2
"""
Governs how much driving along a curved track affects our **accumulated** angle.

The accumulated angle is solely used to scroll the background mountains, and is calculated client-side.

To calculate the change in accumulated angle per second, we multiply this factor by the angle of the track at the current position.

For example, if we are driving along a straight track, the angle is 0, so the accumulated angle will not change.
However, if the angle is 30 degrees, then the accumulated angle will increase by 15 degrees for every second, if this factor is 0.5.
"""

METERS_PER_ANIMATION_FRAME = 3
"""
The number of meters that must be traveled for the road animations to advance by one frame.
"""

ROAD_FRAMES_DIR = "assets/road_frames/"

# hex is 4370ff
SKY_RGB = (67, 112, 255)
BLACK = (0,0,0)

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

FONT_SIZES = {
    "tiny": 16,
    "small": 20,
    "medium": 26,
    "large": 32,
    "huge": 50
}
FONT_TINY = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["tiny"])
FONT_SMALL = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["small"])
FONT_MEDIUM = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["medium"])
FONT_LARGE = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["large"])
FONT_HUGE = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["huge"])

BUTTON_MEDIUM = pygame.image.load("./game/assets/button_medium.png")
""" 240x60 pixels (w x h)"""
BUTTON_LARGE = pygame.image.load("./game/assets/button_large.png")
""" 500x60 pixels (w x h). It's double the size + 40px because of padding. """

MAIN_MENU_BOTTOM_LEFT_TEXT = "By Aidan, Angus, Camila, Michael, and Sindhura"
MAIN_MENU_BOTTOM_RIGHT_TEXT = "Made with Pygame"

HTTP_URL = 'http://localhost:4000'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 3999


CARS = {
    color: pygame.image.load(f'./game/assets/cars/{color}.png') 
    for color in ["red", "orange", "yellow", "green", "blue", "purple", "pink", "white"]
}

# Sounds
sfx_button_hover = pygame.mixer.Sound('./game/assets/sounds/button_hover.mp3')
sfx_button_click = pygame.mixer.Sound('./game/assets/sounds/button_click.mp3')
rev_sound = pygame.mixer.Sound('./game/assets/sounds/rev_engine.mp3')
crash_sound = pygame.mixer.Sound('./game/assets/sounds/crash.mp3')