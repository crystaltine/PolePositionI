import socket
from key_decoder import decode_packet

# Create a server that echoes socket.send() messages in the console

HOST, PORT = "localhost", 3999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Server listening on {HOST}:{PORT}")
while True:
    data, addr = sock.recvfrom(1024)
    print(decode_packet(data[0]))