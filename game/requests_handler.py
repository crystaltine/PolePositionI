import pygame
import socket
import httpx
import threading
from json import loads
from typing import Dict, Callable, Any, Union
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
        
        Also initializes a few basic things
        """
    
        self._listen_stopped = True
        self.registered_events: Dict[str, Callable[[Dict], Any]] = {}
        """ Should be a dict mapping event names to callback functions. """
        
        return
    
    def connect(self, username: str) -> Union[str, None]:
        """
        Creates a socket connection with the server. **Because this contains `socket.recv` calls, it WILL BLOCK THE MAIN THREAD.**
        
        Returns None if connection failed, else returns the client id.
        
        This function also begins the listening thread.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SOCKET_HOST, SOCKET_PORT))
            
            # IMPORTANT: see server/server.py: we need to send the server a username immediately
            self.socket.send(username.encode('utf-8'))
            
            # Receive client id - special event that is sent on connection
            res = self.socket.recv(1024)
            self.client_id = res.decode('utf-8')
            
            self.listen() # now we begin listening for the general format
            
            return self.client_id
        except Exception as e:
            print(f"\x1b[31mError connecting to server: {e}\x1b[0m")
            return None

    def listen(self) -> None:
        """
        Starts a thread that purely listens for messages from the server.
        Since this runs on a different thread, it will not block the main thread.
        
        The main purpose of this is to listen for events such as:
        - game-start (when we should proceed to live game screen)
        - crash (our car crashed, start respawn screen)
        - player-left (when player leaves lobby, and we have to rerender it)
        """
        
        self._listen_stopped = False
        
        def listen_inner():
            while True:
                
                if self._listen_stopped: break

                raw_data = self.socket.recv(1024)
                
                # prefixing: first byte will be a '0' for events, '1' for packet data
                if raw_data[0] == 1: 
                    self.recv_packet(raw_data[1:])
                    continue

                # server sends in data as a JSON string
                payload = loads(raw_data[1:].decode('utf-8'))
                print(f"\x1b[35mEVENT RECV: \x1b[33m{payload}\x1b[0m")
                
                event_name = payload.get('type')
                data = payload.get('data')
                
                _callable = self.registered_events.get(event_name)
                if _callable: _callable(data)
                
        self.listen_thread = threading.Thread(target=listen_inner)
        self.listen_thread.start()
    
    def stop_listening(self) -> None:
        """
        Stops the listening thread. Registered events stay, but won't be called until `listen()` is called again.
        """
        self._listen_stopped = True
    
    def recv_packet(self, data: bytes) -> None:
        """
        @TODO 
        
        Handles a received physics packet from the server.
        
        The data already has prefix byte removed. (so we decode into physics data and update our game)
        """
        print(f"\x1b[35mPACKET RECV: \x1b[33m{data}\x1b[0m")
                
    def on(self, event_name, callback: Callable[[Dict], Any]) -> None:
        """
        Registers a callback function to be called when the specified event is received from the server.
        
        @param event_name: the name of the event to listen for
        @param callback: the function to call when the event is received. The callback function should accept one parameter, which will be JSON-formatted data from server.
        """
        
        self.registered_events[event_name] = callback        

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
            "code": Union[str, None], # will be a 6-digit code if successful
            "message": Union[str, None] # will be an error message if unsuccessful
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
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        
        if not room_id.isdigit():
            return {"success": False, "message": "Room code must be a number."}
        
        res = api_call(f"/joinroom/{self.client_id}/{room_id}")
        print(f"Join room response: {res}")
        return res

    def start_game(self, room_id: int) -> dict:
        """
        Call this function once the user has created their own room and is ready to start.
        
        Requires id passed in as param because I want to avoid circular imports.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        res = api_call(f"/startgame/{self.client_id}/{room_id}")
        print(f"Start game response: {res}")
        return res
    
    def leave_room(self) -> dict:
        """
        Call this function when the user is ready to leave the room.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        res = api_call(f"/leaveroom/{self.client_id}")
        print(f"Leave room response: {res}")
        return res