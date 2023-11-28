import pygame
import socket

HOST, PORT = "localhost", 3999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))

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

def capture_keypress_loop() -> None:
    """
    Run once on game start
    This function listens for the following keys:
    - W, A, S, D
    - Up, Down, Left, Right arrows
    
    On keyDown or keyUp event, prepares a packet to upload to server
    
    ### Packet encoding table:
     
    #### Leftmost bit: 1=keydown, 0=keyup
    
    #### Bits 2 and 3: 00=forward, 01=backward, 10=left, 11=right
    
    - `000` - forward keyup
    - `001` - backward keyup
    - `010` - left keyup
    - `011` - right keyup
    - `100` - forward keydown
    - `101` - backward keydown
    - `110` - left keydown
    - `111` - right keydown
    """
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keyid = id_map[event.key]
            keydown = event.type == pygame.KEYDOWN
            send_packet(keyid, keydown)

def send_packet(keyid: int, keydown: bool) -> None:
    """
    Creates and sends a keyinfo packet to the server.
    Each packet should have a payload size of 3 bits.
    """
    print(f"[debug - send_packet] keyid={keyid}, keydown={keydown}")
    res = sock.send(bytes([keyid | (keydown << 3)]))
    print(f"[debug - send_packet] sent {res} bytes")