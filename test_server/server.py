import sys

sys.path.append('C:\\Users\\s-msheng\\cs\\asp_3\\test_server\\lib')

import socket
import typing
import threading
from time import sleep
from uuid import uuid4

from client import Client, Player, Room
from CONSTANTS import HOST, PORT, TICK_SPEED, TICKS_PER_BROADCAST
from key_decoder import decode_packet
from lib.flask import Flask
from mainloop import broadcast_mainloop

app = Flask(__name__)

#######################################################################

# Room system setup
connected_clients = {}
addresses_to_id = {}
"""
Stores map from client id to Client object (containing socket, host, etc.) for all currently connected clients
Schema: `{int client_id: client.Client client}`
"""

room_data = {}
curr_room_ids = set()
"""
Stores all currently open room IDs 
Schema: `{int room_id: client.Room room}`
"""

def gen_room_id() -> int:
    """ Generates an unused room ID from 0-999999 """
    for i in range(1000000):
        if i not in curr_room_ids:
            curr_room_ids.add(i)
            return i

# REST API endpoints - for room system
@app.route('/checkroom/<int:room_id>')
def checkroom(room_id: int):
    return {"available": room_id not in room_data.keys()}

@app.route('/joinroom/<string:client_id>/<int:room_id>')
def joinroom(client_id: str, room_id: int):
    if room_id not in room_data.keys():
        return {"id": -1, "message": "The requested room does not exist."}

    # Check if user is already connected and present in a room
    if client_id in connected_clients.keys():
        if connected_clients[client_id].room is not None:
            return {"id": -1, "message": f"You are already connected to room {connected_clients[client_id].room}!"}
        else:
            connected_clients[client_id].room = room_id
            room_data[room_id].add_client(connected_clients[client_id])
            return {"id": room_id}

    else:
        return {"success": False, "message": "You do not exist!!!"}

@app.route('/leaveroom/<string:client_id>')
def leaveroom(client_id: str):
    room_id = connected_clients[client_id].room
    if room_id == None:
        return {"success": False}
    
    room_data[room_id].remove(connected_clients[client_id])

    return {"success": True}

@app.route('/createroom/<string:client_id>')
def createroom(client_id: str):
    # Generate room id
    id = gen_room_id()

    if id is None:
        return {"success": False, "message": "Somehow, no rooms are available!"}

    # Required to have already completed initial handshake with socket
    client: typing.Union[Client, None] = connected_clients[bytes(client_id, encoding='utf-8')]
    if not client:
        return {"success": False, "message": "Client has not completed initial socket handshake."}
    
    # If client exists, set its room
    client.room = id

    # Create room object
    room = Room([client], id)
    room_data[id] = room    

    # Return the code
    return {"success": True, "code": f"{id:06d}"}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()

print(f"Socket server listening on {HOST}:{PORT}")

def accept_socket(): 
    while True:
        conn, address = sock.accept()
        print(f"\x1b[36mConnection established\x1b[0m from: \x1b[33m{address}\x1b[0m")
        
        # Send the client a generated ID (sort of like an auth cookie)
        client_id = uuid4().bytes

        # Create a Client object for the connection
        cli = Client(conn, host=address[0], port=address[1], id=client_id)
        connected_clients[client_id] = cli
        addresses_to_id[f"{address[0]}:{address[1]}"] = client_id
        
        # we created an id for them, now emit their id back
        conn.send(client_id)
        
        data, addr = conn.recvfrom(1024)
        on_recv(data, addr)

def apprun(host, port):
    print(f"Flask server running at {host}:{port+1}")
    app.run(host, port+1)

# Create multiprocess to continuously send data to clients, every tick
threading.Thread(target=accept_socket).start()
threading.Thread(target=apprun, args=(HOST, PORT)).start()
threading.Thread(target=broadcast_mainloop, args=(sock, room_data, connected_clients)).start()

def on_recv(data, addr):
    print(f"Received data: {data}")

    # DO STUFF WITH DATA
    # find player based on address
    dhost, daddr = addr
    # clientobj = connected_clients[addresses_to_id[dhost+daddr]]
    
    # Decode received packet
    # keyid, keydown = decode_packet(data)
    
    # Update clientobj with new keypresses
    # This should update the client in its room object as well because of pointers
    # clientobj.update_player_keys(keyid, keydown)