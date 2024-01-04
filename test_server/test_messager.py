import sys
sys.path.append('C:\\Users\\s-msheng\\cs\\asp_3\\test_server\\lib')

import socket
import lib.requests

HOST, SPORT, HPORT = "localhost", 3999, 4000

sock = socket.create_connection(('localhost', 3999))

res = sock.recv(1024)
print(res)

# res should be the client id
res2 = lib.requests.get(f"{HOST}:{HPORT}/").json()
print(f"res2={res2}")