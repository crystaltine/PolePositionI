import array
from typing import List
from socket import socket
import time
from random import shuffle
import threading
import json

from socket_wrapper import _send
from key_decoder import decode_packet
from world.entity import Entity
from world.world import World
from CONSTANTS import *

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
        
        self.stop_receiving = False
        
    def start_recv_thread(self):
        """
        Begins a new thread running recieve loop for the socket.
        Updates the client's corresponding entity if it exists, otherwise does nothing.
        
        This should be used only for in-game keypress packet logic.
        All other requests from the client will be HTTP, not socketio-based. <- i think
        
        ^ Therefore, they shoudln't interfere with this loop.
        """        
            
        print(f"\x1b[34mClient \x1b[33m{self.id}\x1b[0m: Starting recv loop...")
        threading.Thread(target=self.recv_loop).start()
     
    def recv_loop(self):
        while True:
            
            if self.stop_receiving: break
            
            # the client only sends keypress encodings, which are only 0-7 (representable in 1 byte)
            data = None
            try:
                data = self.sock.recv(1)
            except (ConnectionAbortedError, ConnectionResetError):
                print(f"\x1b[34mClient\x1b[33m {self.id}\x1b[31m: Connection aborted!\x1b[0m")
                self.sock.close()
                self.sock = None
                
                print(f"\x1b[34mStopped receiving from Client \x1b[33m{self.id}\x1b[0m!\x1b[0m") 
                del self
                
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
        
    def send_data(self, data, event_name: str = None) -> bool:
        """
        Send a message payload to this Client's registered socket.
        
        ### Important data type notes:
        This function works if `data` is of type: `list`, `dict`, `str`, `bytes`, `bytearray`, `array.array`, `int`, `float`, `bool`
        
        Returns `True` if the socket is still open and the message was sent, `False` if otherwise.
        
        if `event_name` is specified, then the message will be sent as an event, and the data must be JSON-serializable.
        """
        
        if not hasattr(self, "sock") or self.sock is None:
            print(f"\x1b[31mClient \x1b[33m{self.id}\x1b[31m: No socket to send data to!\x1b[0m")
            return False

        # Handle list[float] case, which will be the main use of this function (sending a packet)
        if type(data) == list and event_name is None:
            return _send(self.sock, array.array("f", data)) # no 'event' param, which causes `sock.send` to label the payload as a packet
        
        # other cases
        return _send(self.sock, data, event_name=event_name)
        
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
            num_times_username_taken = self.seen_usernames.count(client.username)
            new_client_username = client.username + (f"-{num_times_username_taken+1}" if num_times_username_taken > 0 else "")
            self.seen_usernames.append(new_client_username)
            
            self.clients[client.id] = {
                "client_obj": client,
                "color": self.available_colors.pop(),
                "username": new_client_username
            }
        
        self.id = id
        self.host = host
        self.started = False
        self.ended = False
        
        # Create the world
        self.world = World()
        
        map_width_one_side = self.world.get_map_data("width")/2
        self.spawn_locations = [
            [90, -3*map_width_one_side/4],
            [60, -2*map_width_one_side/4],
            [30, -map_width_one_side/4],
            [0, 0],
            [30, map_width_one_side/4],
            [60, 2*map_width_one_side/4],
            [90, 3*map_width_one_side/4],
            [120, 4*map_width_one_side/4]
        ] 
        shuffle(self.spawn_locations) # shuffle the spawning locs. First player gets [-1], then [-2], etc. (pop)
        
        # Add all clients to the world
        # testing: put them at (100, 100), (100, 150), (100, 200), and so on.
        # also they should have hitbox radius 10
        for i, client in enumerate(self.clients.values()):
            e = self.world.create_entity(client["username"], client["color"], client["client_obj"], self.spawn_locations.pop(), hitbox_radius=5)
            client["client_obj"].entity = e

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
        
        start_time = time.time() + 5
        
        for client in self.clients.values():
            # see game/screens/waiting_room.py - game-init and leave events dont need extra data.
            send_result = client['client_obj'].send_data({
                "start_timestamp": start_time,
                "init_world_data": self.world.get_world_data() # list of init physics data for each entity
            }, "game-init")
            
            # if not send result, remove client from room
            if not send_result:
                self.remove_client(client['client_obj'])
        
        print(f"Start game: Starting in approx {start_time - time.time()} seconds...")
        
        def delayed_start():
            time.sleep(start_time - time.time())
            
            for client in self.clients.values():
                client['client_obj'].start_recv_thread()  
                
            # also start the game
            self.started = True       
            
            # thread will end here, and the mainloop will start updating physics
        
        # At that time, clients SHOULD ALSO START SENDING KEYBOARD INPUTS.
        # we dont start the loop on start-init otherwise clients can send keypresses before the game starts
        threading.Thread(target=delayed_start).start()

    def add_client(self, client: Client) -> dict:
        """
        Joins a client to the room. Returns their username and color in a dictionary.
        """
        
        num_times_username_taken = self.seen_usernames.count(client.username)
        new_client_username = client.username + (f"-{num_times_username_taken+1}" if num_times_username_taken > 0 else "")
        
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
            send_result = self.clients[client_id]['client_obj'].send_data({
                "username": new_client_username,
                "color": self.clients[client.id]['color']
            }, "player-join")
            
            # if not send result, remove client from room
            if not send_result:
                self.remove_client(client)
            
        # add the new client to the world
        e = self.world.create_entity(new_client_username, self.clients[client.id]['color'], client, self.spawn_locations.pop(), hitbox_radius=5)
        client.entity = e
            
        return { "username": new_client_username, "color": self.clients[client.id]['color'] }
        
    def remove_client(self, client: Client):
        
        # Get that entity's location. (if game already started, then pos will be different, but at that point spawn loc doesnt matter)
        loc = client.entity.pos
        # add their spawn location back into the pool
        self.spawn_locations.append(loc)
        
        # Delete the related entity from the world
        self.world.destroy_entity(client.id)
        
        # add their color back into the pool
        self.available_colors.add(self.clients[client.id]['color'])
        
        # remove their username from the taken list
        leaving_player_username = self.clients[client.id]['username']
        self.seen_usernames.remove(leaving_player_username)
        
        # send the removed client a 'leave' event
        # see game/screens/waiting_room.py - game-init and leave events dont need extra data.
        client.send_data({}, "leave")
        
        # we dont actually care if the client is still connected or not, they get removed anyway
        
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
        
        marked_for_deletion = []
        
        for c in self.clients.values():
            
            # if no sock attribute, remove (it was probably deleted by another check)
            if not hasattr(c["client_obj"], "sock") or c["client_obj"].sock is None:
                marked_for_deletion.append(c["client_obj"])
                continue
            
            if c["client_obj"].sock.fileno() == -1:
                marked_for_deletion.append(c["client_obj"])
        
        # remove all marked clients
        for c in marked_for_deletion:
            self.remove_client(c)
        
        # All dc'ed clients removed, send back new len
        return len(self.clients)
        
    def update_if_started(self) -> None:
        """
        If the game is started, updates the physics of the world.
        
        If game not started yet, do nothing.
        """
        
        if (not self.started) or self.ended: return
        
        game_result = self.world.update()
        
        if game_result:
            # game has ended, perform game-end logic
            self.ended = True # stop updating physics and flag this room as ended
            print(f"\x1b[32mRoom {self.id}'s game has ended!\x1b[0m")
            
            # stop sending packets to each client
            for client in self.clients.values():
                client["client_obj"].stop_receiving = True
            
            # the game-end event should have already been sent to all clients.
            # clients will leave the room from the game-end screen.
            # we don't have to do anything else.
            
    def broadcast_physics(self) -> None:
        """
        If game not started yet, do nothing.
        
        Otherwise, for each socket, send the client the physics data of every entity in the world.
        
        It is assumed that this function will be called inside a tickloop, 
        currently intended for use only in `./mainloop.py` and running once per second.
        
        Returns whether or not data was sent.
        """
        
        current_world_data = self.world.get_world_data()
        
        if not self.started or self.ended: return
        for client in self.clients.values():
            # pre-encode data
            send_result = client["client_obj"].send_data(json.dumps(current_world_data).encode('utf-8'))
            
            if not send_result:
                self.remove_client(client["client_obj"])

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