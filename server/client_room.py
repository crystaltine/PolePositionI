import array
from typing import List
from socket import socket
from time import time, sleep
from sched import scheduler
import threading
import json

from socket_wrapper import _send
from key_decoder import decode_packet
from game_map import GameMap
from world.entity import Entity
from world.world import World
from CONSTANTS import CAR_COLORS

class Client:
    """
    Contains all information related to a connected socket
    
    This can include:
    - `address` (tuple(host, port))
    - The `id` that was generated on the client-side (reverse cookie-like)
    - The ID of the room they are currently connected to
    """
    def __init__(self, sock: socket, host: str = None, port: int = None, id: str = None, room_id: str = None):
        self.sock = sock
        self.address = (host, port)
        self.id = id
        self.room_id = room_id
        self.username = None
        self.entity: Entity = None # The entity that this client controls. If not in game, this should be None
        self.hosting: Room = None # If this client is the owner of a room, this field should point to that room 
        
    def start_recv_thread(self):
        """
        Begins a new thread running recieve loop for the socket.
        Updates the client's corresponding entity if it exists, otherwise does nothing.
        
        This should be used only for in-game keypress packet logic.
        All other requests from the client will be HTTP, not socketio-based. <- i think
        
        ^ Therefore, they shoudln't interfere with this loop.
        
        @TODO - using threading is definitely inefficient, maybe try asyncio?
        """
    
        def recv_loop():
            while True:
                
                # the client only sends keypress encodings, which are only 0-7 (representable in 1 byte)
                data = self.sock.recv(1)
                if data is None: break
                
                keydata = int.from_bytes(data, 'big')
                
                # key data should always be between 0 and 7. If not, ignore
                if keydata < 0 or keydata > 7: 
                    print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m: Ignoring ineligible packet \x1b[33m{keydata}\x1b[0m")
                    continue
                
                # Update keys
                print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m: Updating keys with code \x1b[33m{keydata}\x1b[0m")
                
                if not self.entity is None: 
                    self.entity.update_keys(*decode_packet(keydata))
                else:
                    print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m: No entity to update keys on!")
                
            print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m is disconnected!\x1b[0m")
            
        threading.Thread(target=recv_loop).start()
        
    def send_data(self, data, event_name: str = None) -> bool:
        """
        Send a message payload to this Client's registered socket.
        
        ### Important data type notes:
        This function works if `data` is of type: `list`, `dict`, `str`, `bytes`, `bytearray`, `array.array`, `int`, `float`, `bool`
        
        Returns `True` if the socket is still open and the message was sent, `False` if otherwise.
        
        @TODO - instead of checking types, require data to be `ReadableBuffer`
        """
        try:
            
            # Handle list[float] case, which will be the main use of this function (sending a packet)
            if type(data) == list:
                _send(self.sock, array.array("f", data)) # no 'event' param, which causes `sock.send` to label the payload as a packet
                return True
            
            _send(self.sock, data, event_name=event_name)
            return True
        
        except (ConnectionAbortedError, ConnectionResetError):
            return False
        
    def __str__(self) -> str:
        return f"(Client\x1b[0m id=\x1b[33m{self.id}\x1b[0m, room=\x1b[33m{self.room_id}\x1b[0m)"

class Room:
    def __init__(self, host: Client, clients: List[Client], id: int):
        
        self.available_colors = CAR_COLORS.copy()
        self.seen_usernames = []
        
        self.clients = {}
        
        # Initialize clients. for each client passed in, give them a random color.
        # Also, if their username is taken, add a number suffix to it.
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
        self.started = False
        
        # Pick a random map.
        self.map = GameMap()
        
        # Create the world
        self.world = World(self.map.map_data["world_size"]) # TODO - define track geometry
        
        # Add all clients to the world
        # testing: put them at (100, 100), (100, 150), (100, 200), and so on.
        # also they should have hitbox radius 2.5
        for i, client in enumerate(self.clients.values()):
            self.world.create_entity(client["username"], client["client_obj"], (100, 100 + (50 * i)), hitbox_radius=2.5)

    def start_game(self):
        """
        Initiates game start.
        
        ### Important game flow details:
            - On start request, the server will send a `game-init` event to all clients in the room.
            - This `game-init` also contains an exact timestamp for when the live game will begin.
            - Countdown will be 5 seconds, so the timestamp will be 5 seconds from the calling of this function.
            - After the countdown is over, this function starts the receive loop for all clients, which will start listening for their keyboard inputs.
            - Also, AFTER countdown, marks the room as started, which will allow the mainloop to begin updating physics.
        """
        
        start_time = time() + 5
        
        for client in self.clients.values():
            # see game/screens/waiting_room.py - game-init and leave events dont need extra data.
            client['client_obj'].send_data({"start_time": start_time}, "game-init")
        
        # at start_time, begin the receive loop for all clients
        s = scheduler(time, sleep)
        
        def begin():
            for client in self.clients.values():
                client['client_obj'].start_recv_thread()  
                
            # also start the game
            self.started = True       
        
        # schedule the loop to run at start_time. 
        # At that time, clients SHOULD ALSO START SENDING KEYBOARD INPUTS.
        # we dont start the loop on start-init otherwise clients can send keypresses before the game starts
        s.enterabs(start_time, 1, begin)

    def add_client(self, client: Client) -> dict:
        """
        Joins a client to the room. Returns their username and color in a dictionary.
        """
        
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
            
        return { "username": new_client_username, "color": self.clients[client.id]['color'] }
        
    def remove_client(self, client: Client):
        
        # add their color back into the pool
        self.available_colors.add(self.clients[client.id]['color'])
        
        # remove their username from the taken list
        leaving_player_username = self.clients[client.id]['username']
        self.seen_usernames.remove(leaving_player_username)
        
        # send the removed client a 'leave' event
        # see game/screens/waiting_room.py - game-init and leave events dont need extra data.
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
        If the game is started, updates the physics of the world.
        
        If game not started yet, do nothing.
        
        Returns whether or not updates were made.
        """
        
        if not self.started: return False
        
        self.world.update()
        return True
    
    def broadcast_physics(self) -> None:
        """
        If game not started yet, do nothing.
        
        Otherwise, for each socket, send the client the physics data of every entity in the world.
        
        It is assumed that this function will be called inside a tickloop, 
        currently intended for use only in `./mainloop.py` and running once per second.
        
        Returns whether or not data was sent.
        """
        
        current_world_data = self.world.get_all_data()
        
        if not self.started: return False
        for client in self.clients.values():
            # pre-encode data
            client["client_obj"].send_data(json.dumps(current_world_data).encode('utf-8'))

    def broadcast_event(self, payload: dict, event_name: str):
        """
        Broadcast a message to all clients connected to this room.
        
        Inactive/unresponsive sockets will be automatically removed from the room.
        """
        
        marked_deleted = []
        
        for client_id in self.clients: # every c represents a client id
            client_response = self.clients[client_id]["client_obj"].send_data(payload, event_name)
            
            # if client is no longer connected, remove
            if not client_response:
                marked_deleted.append(client_id) # can't remove due to set
                
        # Update clients
        for client_id in marked_deleted:
            self.clients.pop(client_id)
            
    def disband(self):
        """
        Tells all clients in the room to disconnect, and sets their client objects accordingly.
        """
        print(f"\x1b[35mDisbanding room {self.id}...\x1b[0m")
        
        # "kick" all clients
        for client in self.clients.values():
            print(f"\x1b[35m\tKicking client {client['client_obj'].id}\x1b[0m")
            client["client_obj"].send_data({}, "leave")
            client["client_obj"].room_id = None
            client["client_obj"].hosting = None
            
        