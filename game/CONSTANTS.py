import pygame
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

# hex is 4370ff
SKY_RGB = (67, 112, 255)
BLACK = (0,0,0)

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

FONT_SIZES = {
    "tiny": 16,
    "small": 20,
    "medium": 26,
    "large": 32
}
FONT_TINY = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["tiny"])
FONT_SMALL = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["small"])
FONT_MEDIUM = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["medium"])
FONT_LARGE = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZES["large"])

BUTTON_MEDIUM = pygame.image.load("./game/assets/button_medium.png")
""" 240x60 pixels (w x h)"""
BUTTON_LARGE = pygame.image.load("./game/assets/button_large.png")
""" 500x60 pixels (w x h). It's double the size + 40px because of padding. """

MAIN_MENU_BOTTOM_LEFT_TEXT = "By Aidan, Angus, Camila, Michael, and Sindhura"
MAIN_MENU_BOTTOM_RIGHT_TEXT = "Made with Pygame"

HTTP_URL = 'http://localhost:4000'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 3999