import socket
import typing
import threading
from time import sleep
from uuid import uuid4
import json

from socket_wrapper import PSocket
from server.client_room import Client, Player, Room
from CONSTANTS import HOST, PORT, TICK_SPEED, TICKS_PER_BROADCAST
from key_decoder import decode_packet
import flask
from flask_cors import CORS
from mainloop import broadcast_mainloop

app = flask.Flask(__name__)
# CORS(app)

#######################################################################

# Room system setup
connected_clients: typing.Dict[str, Client] = {} # maps id to Client objs
addresses_to_id = {}
"""
Stores map from client id to Client object (containing socket, host, etc.) for all currently connected clients
Schema: `{int client_id: client.Client client}`
"""

room_data: typing.Dict[int, Room] = {}
curr_room_ids = set()
"""
Stores all currently open room IDs 
Schema: `{int room_id: client.Room room}`
"""

def gen_room_id() -> int:
    """ Generates an unused room ID from 0-999999 """
    
    # TODO - more random room ids, maybe add passwords?
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
        return {"success": False, "message": "The requested room does not exist."}

    # Check if user is already connected and present in a room
    if client_id in connected_clients.keys():
        if connected_clients[client_id].room is not None:
            return {"success": False, "message": f"You are already connected to room {connected_clients[client_id].room}!"}
        else:
            connected_clients[client_id].room = room_id
            room_data[room_id].add_client(connected_clients[client_id])
            
            player_details = [] # send a list of {username: str, color: str, is_host: bool} to the client for lobby display
            for client in room_data[room_id].clients.values():
                player_details.append({"username": client.player.username, "color": client.player.color, "is_host": not (client.hosting is None)})
            
            return {"success": True, "map_data": room_data[room_id].map.map_data, "players": player_details}

    else:
        return {"success": False, "message": "Socket must be registered first."}

@app.route('/leaveroom/<string:client_id>')
def leaveroom(client_id: str):
    client = connected_clients.get(client_id)
    
    if not client:
        return {"success": False, "message": "Socket must be registered first."}
    
    room_id = client.room
    if room_id == None:
        return {"success": False, "message": "You are not currently in a room."}
    
    # TODO - if the client is the host, disband the room (OR give someone else host)
    
    room_data[room_id].remove(connected_clients[client_id])
    client.room = None

    return {"success": True}

@app.route('/createroom/<string:client_id>')
def createroom(client_id: str):
    # Generate room id
    id = gen_room_id()

    if id is None:
        return {"success": False, "message": "Somehow, no rooms are available!"}

    # Required to have already completed initial handshake with socket
    client: typing.Union[Client, None] = connected_clients.get(client_id)
    if not client:
        return {"success": False, "message": "Client has not completed initial socket handshake."}
    
    # If client exists, set its room
    client.room = id

    # Create room object
    room = Room(client, [client], id)
    room_data[id] = room    
    client.hosting = room # mark this client as the host of this room

    # Return the code
    return {"success": True, "code": f"{id:06d}", "map_data": room.map.map_data}

@app.route('/startgame/<string:client_id>/<int:room_id>')
def startgame(client_id: str, room_id: int):
    # First, verify that client_id is currently in AND IS THE HOST of room_id
    client = connected_clients.get(client_id)
    
    if not client or not client.hosting.id == room_id:
        # error unauthenticated
        return {"success": False, "message": "Unauthorized attempt to start game"}
    
    # They are the host of the room, Mark the room as started
    room = room_data.get(room_id)
    if not room:
        return {"success": False, "message": f"Room {room_id} does not exist."}
    
    room.start_game()
    return {"success": True, "message": f"Room {room_id} marked as started and recv loops initiated."}

sock = PSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
sock.bind((HOST, PORT))
sock.listen()   

print(f"Socket server listening on {HOST}:{PORT}")

def accept_socket(): 
    """
    This handles the initial handshake between the client and the server.
    Registers the socket and assigns a client id to the connection.
    """
    while True:
        conn, address = sock.accept()
        conn = PSocket(conn)
        print(f"\x1b[36mConnection established\x1b[0m from: \x1b[33m{address}\x1b[0m")
        
        # Send the client a generated ID (sort of like an auth cookie)
        client_id = uuid4().hex

        # Create a Client object for the connection. Currently HAS NO USERNAME (see below)
        cli = Client(conn, host=address[0], port=address[1], id=client_id)
        connected_clients[client_id] = cli
        addresses_to_id[f"{address[0]}:{address[1]}"] = client_id
        
        # IMPORTANT - the client side's `socket_man.connect()` must handle this (send a username!!!)
        # ALSO IMPORATNT - we call this recv before sending the client id, since the client
        # sends data before recv'ing. its 3 am and i cant think clearly but im guessing the order of these
        # lines must corresponsd (recv on server <-> send on client and vice versa) because of thread blocking
        username = conn.recv(1024).decode('utf-8') # wait for client to send back their username
        
        # we created an id for them, now emit their id back
        # THIS IS A SPECIAL EVENT - does not get handled by event listener
        # since the client SHOULD NOT HAVE BEGUN THE EVENT LISTENER YET. (it happens immediately after recv. this)
        conn.send_raw(client_id.encode('utf-8'))
        
        # TODO - if invalid, kick them or something/ask for a new username
        cli.player.username = username

def apprun(host, port):
    print(f"Flask server running at {host}:{port+1}")
    app.run(host, port+1)

# Create multiprocess to continuously send data to clients, every tick
threading.Thread(target=accept_socket).start()
threading.Thread(target=apprun, args=(HOST, PORT)).start()
threading.Thread(target=broadcast_mainloop, args=(sock, room_data, connected_clients)).start()