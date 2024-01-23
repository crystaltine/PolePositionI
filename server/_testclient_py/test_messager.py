import socket
import threading
from time import sleep
import httpx

HOST, SPORT, HPORT = "localhost", 3999, 4000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, SPORT))

res = sock.recv(1024)
client_id = res.decode('utf-8')
print(f">>> Client id: \x1b[33m{client_id}\x1b[0m")

sleep(3)
res = httpx.get(f"http://localhost:{HPORT}/createroom/{client_id}")
print(f"Create room response: {res.json()}")

def recv_messages():
    while True:
        data = sock.recv(1024)
        print(f"Receive loop: \x1b[33m{data}\x1b[0m")

threading.Thread(target=recv_messages).start()