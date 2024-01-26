import pygame
import socket
import httpx
from time import sleep
from CONSTANTS import id_map, HTTP_URL, SOCKET_HOST, SOCKET_PORT

def api_call(endpoint: str, query_params: dict = None) -> dict:
    """
    (internal) Makes a GET request to the server.
    
    @param endpoint: the endpoint to call, e.g. `createroom` (no leading slash)
    @param query_params: a `dict` of query parameters to pass to the endpoint.
    
    @returns: a JSON/`dict` containing the response data
    """
    
    query_params_string = ""
    if query_params:
        query_params_string = "?" + "&".join([f"{key}={val}" for key, val in query_params.items()])
    try:
        res = httpx.get(f"{HTTP_URL}/{endpoint}{query_params_string}")
        return res.json()
    except Exception as e:
        print(f"\x1b[31mError making API call: {e}\x1b[0m")
        return {"success": False, "message": f"Couldn't connect to the server."}

class SocketManager:
    """
    Handles all the client-server socket-tick processes, including:
    - Listening for movement key presses
    - Sending packets to server containing that key data
    - Listening for physics data from server side
    """
    
    def __init__(self):
        """
        Simply creates a pointer to this future object.
        """
        return
    
    def connect(self):
        """
        Creates a socket connection with the server.
        """
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SOCKET_HOST, SOCKET_PORT))

        # Receive client id
        res = sock.recv(1024)
        client_id = res.decode('utf-8')
        
        self.client_id = client_id
        self.socket = sock

    def handle_game_keypresses(self, event) -> None:
        """
        ### Must run INSIDE a `for event in pygame.event.get()` loop.
        
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
        
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keyid = id_map.get(event.key)
            if not keyid: return
            keydown = event.type == pygame.KEYDOWN
            self.send_packet(keyid, keydown)

    def send_packet(self, keyid: int, keydown: bool) -> None:
        """
        Creates and sends a keyinfo packet to the server.
        Each packet should have a payload size of 3 bits.
        """
        keydata = keyid | (keydown << 2)
        print(f"Creating&sending packet with keyid={keyid}, keydown={keydown}")
        self.socket.send(keydata.to_bytes(4, 'big'))
        
    def send_event(self, event_name: str) -> None:
        """
        Sends an event to the server.
        
        ### Event names:
        - `start_game`
        - `leave_room`
        """
        self.socket.send(event_name.encode('utf-8'))

    def recv_packet(self):
        """
        Receives a packet from the server.
        
        @TODO - server response format changed - update this function
        
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
    
class HTTPManager:
    """
    ### Initialize after SocketManager instance is created and client id is obtained.
    
    Contains functions that handle all client-side services that have to do with HTTP requests, 
    such as creating rooms, joining rooms, receiving scores, etc.
    """
    
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
    
    def create_room(self) -> dict:
        """
        Uses the client id obtained from initalization to create a room.
        If the request is successful, the client will be automatically added to the room.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "code": str | None, # will be a 6-digit code if successful
            "message": str | None # will be an error message if unsuccessful
        }
        ```
        """
        room_data = api_call(f"/createroom/{self.client_id}")
        print(f"Create room response: {room_data}")
        return room_data

    def join_room(self, room_id: str) -> dict:
        """
        Sends a join room request to the server.
        Provide a room id from an input field that the user types in.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": str | None # will be an error message if unsuccessful
        }
        ```
        """
        
        if not room_id.isdigit():
            return {"success": False, "message": "Room code must be a number."}
        
        res = api_call(f"/joinroom/{self.client_id}/{room_id}")
        print(f"Join room response: {res}")
        return res

    @staticmethod
    def start_game(self, room_id: int) -> dict:
        """
        Call this function once the user has created their own room and is ready to start.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": str | None # will be an error message if unsuccessful
        }
        ```
        """
        res = api_call(f"/startgame/{self.client_id}/{room_id}")
        print(f"Start game response: {res}")
        return res
    
    @staticmethod
    def leave_room(self) -> dict:
        """
        Call this function when the user is ready to leave the room.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": str | None # will be an error message if unsuccessful
        }
        ```
        """
        res = api_call(f"/leaveroom/{self.client_id}")
        print(f"Leave room response: {res}")
        return res