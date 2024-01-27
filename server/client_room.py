import array
from typing import List

from socket import socket
from socket_wrapper import _send
from key_decoder import decode_packet
from key_press import Player
from game_map import GameMap
from CONSTANTS import CAR_COLORS

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
        
    def send_data(self, data, event_name: str = None) -> bool:
        """
        Send a message payload to this Client's registered socket.
        
        Returns `True` if the socket is still open and the message was sent, `False` if otherwise.
        """
        try:
            
            # Handle list[float] case, which will be the main use of this function (sending a packet)
            if type(data) == list:
                _send(self.sock, array.array("d", data)) # no 'event' param, which causes `sock.send` to label the payload as a packet
                return True
            
            # Encode if string, else just construct bytes. Send as event if provided
            _send(self.sock, bytes(data, 'utf-8') if type(data) == str else bytes(data), event_name=event_name)
            return True
        except (ConnectionAbortedError, ConnectionResetError):
            return False
        
    def __str__(self) -> str:
        return f"(Client\x1b[0m addr=\x1b[33m{self.address}\x1b[0m, id=\x1b[33m{self.id}\x1b[0m, room=\x1b[33m{self.room}\x1b[0m)"

class Room:
    def __init__(self, host: Client, clients: List[Client], id: int):
        
        self.available_colors = CAR_COLORS.copy()
        self.seen_usernames = []
        
        self.clients = {}
        
        # Initialize clients. for each client passed in, give them a random color.
        for client in clients:
            
            # Handle repeat usernames (add a number suffix)
            num_times_username_taken = self.seen_usernames.count(client.player.username)
            new_client_username = client.player.username + (f"-{num_times_username_taken+1}" if num_times_username_taken > 0 else "")
            self.seen_usernames.append(new_client_username)
            
            self.clients[client.id] = {
                "client_obj": client,
                "color": self.available_colors.pop(),
                "username": new_client_username
            }
        
        self.id = id
        self.host = host
        self.started = False # TODO - if started, start data receive loop
        
        # Pick a random map.
        self.map = GameMap()

    def start_game(self):
        """
        Marks the room as started (sets `self.started = True`) and begins receive loop from clients
        """
        self.started = True
        for client in self.clients.values():
            # see game/screens/waiting_room.py - game-start and leave events dont need extra data.
            client['client_obj'].send_data({}, "game-start")

    def add_client(self, client: Client):
        
        num_times_username_taken = self.seen_usernames.count(client.player.username)
        new_client_username = client.player.username + (f"-{num_times_username_taken+1}" if num_times_username_taken > 0 else "")
        
        self.clients[client.id] = {
            "client_obj": client,
            "color": self.available_colors.pop(),
            "username": new_client_username
        }
        
        # add their username to the taken list
        self.seen_usernames.append(new_client_username)
        
        # send the 'player-join' event to all other clients in the room, with the new client's username and color
        for client_id in self.clients:
            if client_id == client.id: continue
            self.clients[client_id]['client_obj'].send_data({
                "username": new_client_username,
                "color": self.clients[client.id]['color']
            }, "player-join")
        
    def remove_client(self, client: Client):
        
        # add their color back into the pool
        self.available_colors.add(self.clients[client.id]['color'])
        
        # remove their username from the taken list
        leaving_player_username = self.clients[client.id]['username']
        self.seen_usernames.remove(leaving_player_username)
        
        # send the removed client a 'leave' event
        # see game/screens/waiting_room.py - game-start and leave events dont need extra data.
        client.send_data({}, "leave")
        
        # remove them from the room
        # note - the `Client` object shouldn't be destroyed because of Python's garbage collector maintaining a nonzero reference count
        # We can try testing this out later, for now just be safe and set to None
        # del self.clients[client.id]
        self.clients.pop(client.id)
        
        # send the 'player-leave' event to all other clients in the room, with the client's username
        for client_id in self.clients:
            self.clients[client_id]['client_obj'].send_data({
                "username": leaving_player_username
            }, "player-leave")
        
    def num_connected(self):
        """
        Returns the number of clients connected to the room.
        
        This also performs internal checks to see which clients are still connected. All disconnected sockets will be removed.
        """
        for c in self.clients.values():
            print(f"room {self.id}: a client has fileno {c['client_obj'].sock.fileno()}")
            if c["client_obj"].sock.fileno() == -1:
                self.remove_client(c["client_obj"])
        
        # All dc'ed clients removed, send back new len
        return len(self.clients)
        
    def update_if_started(self) -> bool:
        """
        If the game is started, updates the physics of all players in the room using their current velocity and acceleration.
        
        If game not started yet, do nothing.
        
        Returns whether or not updates were made.
        """
        
        if not self.started: return False
        
        for client in self.clients.values():
            client["client_obj"].update_player()
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
        for client in self.clients.values():
            client["client_obj"].send_data(client["client_obj"].player.get_physics_data())

    def broadcast_all(self, data):
        """
        Broadcast a message to all clients connected to this room.
        
        Inactive/unresponsive sockets will be automatically removed from the room.
        """
        
        marked_deleted = []
        
        for client_id in self.clients: # every c represents a client id
            client_response = self.clients[client_id]["client_obj"].send_data(data)
            
            # if client is no longer connected, remove
            if not client_response:
                marked_deleted.append(client_id) # can't remove due to set
                
        # Update clients
        for client_id in marked_deleted:
            self.clients.pop(client_id)