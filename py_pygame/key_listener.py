import pygame
import socket

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

class SocketManager:
    """
    Handles all the client-server socket-tick processes, including:
    - Listening for movement key presses
    - Sending packets to server containing that key data
    - Listening for physics data from server side
    
    Socket connection must be created separately and provided to constructor.
    """

    def __init__(self, socket: socket.socket) -> None:
        self.socket = socket

    def capture_keypress_loop(self) -> None:
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
                self.send_packet(keyid, keydown)

    def send_packet(self, keyid: int, keydown: bool) -> None:
        """
        Creates and sends a keyinfo packet to the server.
        Each packet should have a payload size of 3 bits.
        """
        keydata = keyid | (keydown << 2)
        print(f"Creating&sending packet with keyid={keyid}, keydown={keydown}")
        res = self.socket.send(keydata.to_bytes(4, 'big'))

    def recv_packet(self):
        """
        Receives a packet from the server.
        
        Each packet contains the following data:
        - x pos: int
        - y pos: int
        - x vel: int
        - y vel: int
        - x acc: int
        - y acc: int
        
        In total, 6 ints, so 24 bytes of data.
        """
        data = self.socket.recv(24)
        print(f"\x1b[35mserver->client: \x1b[33m{data}\x1b[0m")
        return data