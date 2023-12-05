import socket
from key_decoder import decode_packet
from time import sleep
import threading
from packet_distr import broadcast_mainloop

TICK_SPEED = 24
TICKS_PER_BROADCAST = 24
HOST, PORT = "localhost", 3999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Socket server listening on {HOST}:{PORT}")

# Create multiprocess to continuously send data to clients, every tick
threading.Thread(target=broadcast_mainloop, args=(packet, addresses)).start()

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received data: {data}")