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

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

FONT_SIZE = 26
FONT = pygame.font.Font('./game/assets/LemonMilk_MedItalic.otf', FONT_SIZE)

BUTTON_MEDIUM = pygame.image.load("./game/assets/button_medium.png")
""" 240x60 pixels (w x h)"""
BUTTON_LARGE = pygame.image.load("./game/assets/button_large.png")
""" 500x60 pixels (w x h). It's double the size + 40px because of padding. """

HTTP_URL = 'http://localhost:4000'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 3999