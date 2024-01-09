import socket
from time import sleep
from client import Room, Client
from typing import Dict

from CONSTANTS import HOST, PORT, TICK_SPEED, TICKS_PER_BROADCAST

def broadcast_mainloop(sock: socket.socket, rooms: Dict[int, Room], connected_clients: Dict[str, Client]) -> None:
    """
    Sends the specified packet to all specified addresses.
    Likely usage will be to send a packet to both (or multiple) clients connected to a room

    Args:
    addresses: list of addresses to send to
    packet: data to send
    sock: socket object running on server
    """

    # Run stuff here

    counter = 0

    while True:
        sleep(1 / TICK_SPEED)

        # TICK CLIENT DATA FOR EVERY ROOM (physics stuff)
        # print(f"Server Tick. Counter: {counter}")

        counter += 1    
        if counter == TICKS_PER_BROADCAST:
            counter = 0
            
            # FOR EACH ROOM, DO STUFF!!!
            for room in rooms.values():
                
                num_connected = room.num_connected()
                if num_connected == 0:
                    print(f"\x1b[31mNot broadcasting to room {room.id} because it has no connected clients.\x1b[0m")
                else:
                    print(f"Broadcasting to {num_connected} sockets in room {room.id}") 
                    room.broadcast_all(f"[Server] You are in room: {room.id} with {num_connected-1} other players connected.") 
                            