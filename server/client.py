from socket import socket
from typing import List
from key_decoder import decode_packet
from key_press import Player
import array

class Client:
    """
    Contains all information related to a connected socket
    
    This can include:
    - `address` (tuple(host, port))
    - The `id` that was generated on the client-side (reverse cookie-like)
    - The ID of the room they are currently connected to
    - A `key_press.Player` object that stores data about the player, like pos, vel, and acc
    """
    def __init__(self, sock: socket, host: str = None, port: int = None, id: str = None, room: int = None):
        self.sock = sock
        self.address = (host, port)
        self.id = id
        self.room = room
        self.player = Player()
        self.hosting: Room = None # If this client is the owner of a room, this field should point to that room 

    def update_player(self):
        self.player.update()
        
    def begin_receiving_data(self):
        while True:
            print(f"PLS GIVE ME DATAA")
            keydata = int.from_bytes(self.sock.recv(4), 'big')
            print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m: Received data \x1b[33m{keydata}\x1b[0m")
            self.update_player_keys(*decode_packet(keydata))

    def update_player_keys(self, keyID: int, down: bool):
        """
        Updates player data with new keypress data received from them
        """
        self.player.num_processing(keyID, down)
        print(f"\x1b[35mPLAYER UPDATING! keyID={keyID}, down={down}")
        
    def send_msg(self, msg) -> bool:
        """
        Send a message payload to this Client's registered socket.
        
        Returns `True` if the socket is still open and the message was sent, `False` if otherwise.
        """
        try:
            
            # Handle list[float] case, which will be the main use of this function
            if type(msg) == list:
                self.sock.send(array.array("d", msg))
                return True
            
            # Encode if string, else just construct bytes
            self.sock.send(bytes(msg, 'utf-8') if type(msg) == str else bytes(msg))
            return True
        except (ConnectionAbortedError, ConnectionResetError):
            return False
        
    def __str__(self) -> str:
        return f"(Client\x1b[0m addr=\x1b[33m{self.address}\x1b[0m, id=\x1b[33m{self.id}\x1b[0m, room=\x1b[33m{self.room}\x1b[0m)"

class Room:
    def __init__(self, host: Client, clients: List[Client], id: int):
        self.clients = set(clients)
        self.id = id
        self.host = host
        self.started = False # TODO - if started, start data receive loop

    def start_game(self):
        """
        Marks the room as started (sets `self.started = True`) and begins receive loop from clients
        """
        self.started = True
        for client in self.clients:
            client.begin_receiving_data()

    def add_client(self, client: Client):
        self.clients.add(client)
        
    def num_connected(self):
        """
        Returns the number of clients connected to the room.
        
        This also performs internal checks to see which clients are still connected. All disconnected sockets will be removed.
        """
        for c in self.clients:
            if c.sock.fileno() == -1:
                self.remove_client(c)
        
        # All dc'ed clients removed, send back new len
        return len(self.clients)        

    def remove_client(self, client: Client):
        self.clients.remove(client)
        
    def update_if_started(self) -> bool:
        """
        If the game is started, updates the physics of all players in the room using their current velocity and acceleration.
        
        If game not started yet, do nothing.
        
        Returns whether or not updates were made.
        """
        
        if not self.started: return False
        
        for client in self.clients:
            client.update_player()
        return True
    
    def broadcast_physics(self) -> None:
        """
        If game not started yet, do nothing.
        
        Otherwise, for each socket, send the client their current, updated physics data.
        
        It is assumed that this function will be called inside a tickloop, 
        currently intended for use only in `./mainloop.py` and running once per second.
        
        Returns whether or not data was sent.
        """
        if not self.started: return False
        for client in self.clients:
            client.send_msg(client.player.get_physics_data())

    def broadcast_all(self, data):
        """
        Broadcast a message to all clients connected to this room.
        
        Inactive/unresponsive sockets will be automatically removed from the room.
        """
        
        marked_deleted = []
        
        for c in self.clients: # every c represents a client obj
            client_response = c.send_msg(data)
            
            # if client is no longer connected, remove
            if not client_response:
                marked_deleted.append(c) # can't remove due to set
                
        # Update clients
        self.clients.difference_update(marked_deleted)