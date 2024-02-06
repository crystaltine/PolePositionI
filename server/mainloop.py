from socket import socket
from time import sleep, time_ns
from client_room import Room, Client
from typing import Dict

from CONSTANTS import TICK_SPEED, TICKS_PER_BROADCAST

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
            
            marked_disbanded = []
            for room in id_to_room.values():
                
                num_connected = room.num_connected()
                if num_connected == 0:
                    print(f"\x1b[31mDisbanding room {room.id} because it has no connected clients.\x1b[0m")
                    # disband room
                    marked_disbanded.append(room.id)
                else:
                    print(f"\x1b[35m{room.id}\x1b[0m: {num_connected} players, started={room.started}, ended={room.ended}")
                    
                    if not room.ended:
                        room.broadcast_physics()
                    
                    # DEBUG: print short physics info
                    for client in room.clients.values():
                        c: Client = client["client_obj"]
                        print(f"\t{c.entity.color}:\x1b[33m p=[{c.entity.pos[0]:.3f},{c.entity.pos[1]:.3f}] v={c.entity.vel:.3f} a={c.entity.acc:.3f}, theta={c.entity.angle:.3f}, is_crashed={c.entity.crash_end_timestamp > time_ns()/1e9}\x1b[0m")
            
            # disband rooms
            for room_id in marked_disbanded:
                del id_to_room[room_id]
                print(f"\x1b[31mDisbanded (deleted) empty room {room_id}.\x1b[0m")
                                   