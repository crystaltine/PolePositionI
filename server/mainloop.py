from socket_wrapper import _send
from socket import socket
from time import sleep
from client_room import Room, Client
from typing import Dict

from CONSTANTS import HOST, PORT, TICK_SPEED, TICKS_PER_BROADCAST

def broadcast_mainloop(id_to_room: Dict[str, Room], id_to_client: Dict[str, Client]) -> None:
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

        for room in id_to_room.values():
            room.update_if_started()

        counter += 1    
        if counter == TICKS_PER_BROADCAST:
            counter = 0
            
            # FOR EACH ROOM, DO STUFF!!!
            for room in id_to_room.values():
                
                num_connected = room.num_connected()
                if num_connected == 0:
                    print(f"\x1b[31mNot broadcasting to room {room.id} because it has no connected clients.\x1b[0m")
                else:
                    print(f"\x1b[35m{room.id}\x1b[0m: {num_connected} players, started={room.started}, ended={room.ended}")
                    
                    if not room.ended:
                        room.broadcast_physics()
                    
                    # DEBUG: print short physics info
                    for client in room.clients.values():
                        c: Client = client["client_obj"]
                        print(f"\t{c.id}:\x1b[33m p=[{c.entity.pos[0]:.3f},{c.entity.pos[1]:.3f}] v={c.entity.vel:.3f} a={c.entity.acc:.3f}, theta={c.entity.angle:.3f}\x1b[0m")
                            