import socket
from time import sleep
from CONSTANTS import TICK_SPEED, TICKS_PER_BROADCAST, PORT, HOST

def broadcast_mainloop(sock: socket.socket, packet: bytes, addresses: list) -> None:
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

        # TICK CLIENT DATA (physics stuff)
        print(f"Server Tick. Counter: {counter}")

        counter += 1    
        if counter == TICKS_PER_BROADCAST:
            counter = 0

            print("[mainloop] Broadcasting packet to given addresses...")
            for address in addresses:
                sock.sendto(packet, address)