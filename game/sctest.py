import pygame
import sys
from key_listener import SocketManager
import socket
import threading
sys.path.append('C:\\Users\\s-msheng\\cs\\asp_3\\server\\lib')

HOST, SPORT, HPORT = "localhost", 3999, 4000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, SPORT))

# Receive client id
# TODO - this request should be completed after the main menu screen, but this is just a test without that
res = sock.recv(1024)
client_id = res.decode('utf-8')

pygame.init()

running = True
   
SKY = (97, 120, 232)

width = 1000    
height = 700

screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")
grass = pygame.image.load('./assets/grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height//3)))
mtns = pygame.image.load('./assets/mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height//5))
FPS = pygame.time.Clock()
#player = User(Sprite) insert sprite later

socket_manager = SocketManager(sock, client_id)

#call object instances outside the loop
while running:
    FPS.tick(24) #moved timer into loop
    screen.blit(grass, (0, 2*height//5))
    screen.blit(mtns, (0, height//5))
        
    socket_manager.capture_keypress_loop()
        
    pygame.display.update()

    #key numbers for keydowbs binary onkeyevent -> send to server
    #up: 00
    #down: 01
    #left: 10
    #right: 11

    #keydown: 1##
    #keyup: 0##

   
pygame.quit()
sys.exit()
