import socket
from key_decoder import decode_packet
from time import sleep
import threading
from mainloop import broadcast_mainloop
from CONSTANTS import TICK_SPEED, TICKS_PER_BROADCAST, PORT, HOST

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

# TEMP
packet = 'hewwo'
addresses = []

print(f"Socket server listening on {HOST}:{PORT}")

# Create multiprocess to continuously send data to clients, every tick
threading.Thread(target=broadcast_mainloop, args=(sock, packet, addresses)).start()

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received data: {data}")