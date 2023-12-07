import socket

HOST, PORT = "localhost", 3999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))

while True:
    msg = input()
    sock.send(bytes(msg, "utf-8"))