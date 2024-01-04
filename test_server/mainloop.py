import socket
from time import sleep
from client import Room

from CONSTANTS import HOST, PORT, TICK_SPEED, TICKS_PER_BROADCAST

def broadcast_mainloop(sock: socket.socket, rooms: dict, connected_clients) -> None:
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
            
            for item in connected_clients.values():
                print(f"\x1b[36mConnected Client: {item }\x1b[0m")  
            
            # FOR EACH ROOM, DO STUFF!!!
            for room in rooms.values():
                room: Room
                print(f"broadcasting to room: id={room.id}")
                room.broadcast_all(sock, bytes("Hello from a server that doesn't work!",encoding="utf-8"))
            print("--------------------------------------------------------------")
                            