import sys
sys.path.append('C:\\Users\\s-msheng\\cs\\asp_3\\test_server\\lib')

import socket

HOST, PORT = 'localhost', 3999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))

sock.listen(10)
conn, address = sock.accept()  # accept new connection
print("Connection from: " + str(address))
conn.send(bytes('YOU SUCK L GET BETTER AT PYTHON', 'utf-8'))