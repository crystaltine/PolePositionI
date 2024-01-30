import socket
import typing
import threading
import random
from string import ascii_uppercase, digits
from uuid import uuid4

from socket_wrapper import _send
import client_room
from CONSTANTS import HOST, PORT
import flask
from mainloop import broadcast_mainloop

app = flask.Flask(__name__)
# CORS(app)

#######################################################################

# Room system setup
id_to_client: typing.Dict[str, client_room.Client] = {} # maps id to Client objs
"""
Stores map from client id to Client object (containing socket, host, etc.) for all currently connected clients
Schema: `{int client_id: client.Client client}`
"""

id_to_room: typing.Dict[str, client_room.Room] = {}
"""
Stores all currently open room IDs 
Schema: `{str room_id: client.Room room}`
"""

def gen_room_id() -> str:
    """
    Generate a random room ID that is not currently in use.
    Room IDs are 6-character long strings with the following characters allowed:
    A-Z, 0-9
    """
    
    characters = ascii_uppercase + digits
    random_string = ''.join(random.choice(characters) for i in range(6))
    
    try_count = 0
    while random_string in id_to_room.keys():
        if try_count > 100:
            return None
        random_string = ''.join(random.choice(characters) for i in range(6))

    return random_string

# REST API endpoints - for room system
@app.route('/checkroom/<string:room_id>')
def checkroom(room_id: str):
    return {"available": room_id not in id_to_room.keys()}

@app.route('/joinroom/<string:client_id>/<string:room_id>')
def joinroom(client_id: str, room_id: str):
    if room_id not in id_to_room.keys():
        return {"success": False, "message": "The requested room does not exist."}

    # Check if user is already connected and present in a room
    if client_id in id_to_client.keys():
        if id_to_client[client_id].room_id is not None:
            return {"success": False, "message": f"You are already connected to room {id_to_client[client_id].room_id}!"}
        
        if id_to_room[room_id].started:
            return {"success": False, "message": f"Room {room_id} has already started!"}
        
        if len(id_to_room[room_id].clients) >= 8: 
            # "disconnected" clients still count towards the 8 max 
            return {"success": False, "message": f"Room {room_id} is full! (8 max)"}
        
        else:
            id_to_client[client_id].room_id = room_id
            
            this_player_info = id_to_room[room_id].add_client(id_to_client[client_id])
            
            player_details = [] 
            # send a list of {username: str, color: str, is_host: bool} to the client for lobby display
            # this is a list of all players in the room, including the user themselves
            for client_id in id_to_room[room_id].clients:
                player_details.append({
                    "username": id_to_room[room_id].clients[client_id]["username"],
                    "color": id_to_room[room_id].clients[client_id]["color"],
                    "is_host": not (id_to_room[room_id].clients[client_id]["client_obj"].hosting is None)
                })
            
            return {
                "success": True, 
                "map_data": id_to_room[room_id].world.get_map_data(),
                "players": player_details,
                "code": room_id,
                "username": this_player_info["username"],
                "color": this_player_info["color"],
            }

    else:
        return {"success": False, "message": "Socket must be registered first (try restarting your game)."}

@app.route('/leaveroom/<string:client_id>')
def leaveroom(client_id: str):
    client = id_to_client.get(client_id)
    
    if not client:
        return {"success": False, "message": "Socket must be registered first (try restarting your game)."}
    
    room_id = client.room_id
    if room_id == None:
        return {"success": False, "message": "You are not currently in a room."}
    
    room = id_to_room.get(room_id)
    
    # If the client is the host, disband the room
    if client.hosting is room or (room.num_connected() == 1):
        room.disband()
        del id_to_room[room_id] # use del to trigger the __del__ method of the room (which handles telling all clients to disconnect)
        return {"success": True, "message": f"Successfully disbanded room {room_id}."}
    
    room.remove_client(id_to_client[client_id])
    
    # if nobody is left in the room and room.ended is True, delete the room
    if room.num_connected() == 0 and room.ended:
        del id_to_room[room_id]
    
    client.room_id = None
    return {"success": True, "message": f"Successfully left room {room_id}."}

@app.route('/createroom/<string:client_id>')
def createroom(client_id: str):
    # Generate room id
    id = gen_room_id()

    if id is None:
        return {"success": False, "message": "Somehow, no rooms are available!"}

    # Required to have already completed initial handshake with socket
    client: typing.Union[client_room.Client, None] = id_to_client.get(client_id)
    if not client:
        return {"success": False, "message": "Client has not completed initial socket handshake (try restarting your game)."}
    
    # If client exists, set its room
    client.room_id = id

    # Create room object
    room = client_room.Room(client, [client], id)
    id_to_room[id] = room    
    client.hosting = room # mark this client as the host of this room

    # Return the code
    return {
        "success": True, 
        "code": f"{id}",
        "map_data": room.world.get_map_data(),
        "player_data": { # return the user themselves
            "username": room.clients[client_id]["username"],
            "color": room.clients[client_id]["color"],
            "is_host": True
        }
    }

@app.route('/startgame/<string:client_id>/<string:room_id>')
def startgame(client_id: str, room_id: str):
    # First, verify that client_id is currently in AND IS THE HOST of room_id
    client = id_to_client.get(client_id)
    
    if not client or not client.hosting.id == room_id:
        # error unauthenticated
        return {"success": False, "message": "Unauthorized attempt to start game"}
    
    # They are the host of the room, Mark the room as started
    room = id_to_room.get(room_id)
    if not room:
        return {"success": False, "message": f"Room {room_id} does not exist."}
    
    room.start_game()
    return {"success": True, "message": f"Room {room_id} marked as started and recv loops initiated."}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print(f"\x1b[36mConnection established\x1b[0m from: \x1b[33m{address}\x1b[0m")
        
        # Send the client a generated ID (sort of like an auth cookie)
        client_id = uuid4().hex

        # Create a Client object for the connection. Currently HAS NO USERNAME (see below)
        cli = client_room.Client(conn, host=address[0], port=address[1], id=client_id)
        id_to_client[client_id] = cli
        
        # IMPORTANT - the client side's `socket_man.connect()` must handle this (send a username!!!)
        # ALSO IMPORATNT - we call this recv before sending the client id, since the client
        # sends data before recv'ing. its 3 am and i cant think clearly but im guessing the order of these
        # lines must corresponsd (recv on server <-> send on client and vice versa) because of thread blocking
        username = conn.recv(1024)
        
        if not username:
            # client disconnected before sending username
            print(f"\x1b[31mClient \x1b[33m{client_id}\x1b[31m disconnected before sending username\x1b[0m")
        
        username = username.decode('utf-8') # wait for client to send back their username
        
        # we created an id for them, now emit their id back
        # THIS IS A SPECIAL EVENT - does not get handled by event listener
        # since the client SHOULD NOT HAVE BEGUN THE EVENT LISTENER YET. (it happens immediately after recv. this)
        conn.send(client_id.encode('utf-8'))
        
        # TODO - if invalid, kick them or something/ask for a new username
        cli.username = username

def apprun(host, port):
    print(f"Flask server running at {host}:{port+1}")
    app.run(host, port+1)

# Create multiprocess to continuously send data to clients, every tick
thread_accept = threading.Thread(target=accept_socket, daemon=True)
thread_accept.start()

thread_flask = threading.Thread(target=apprun, args=(HOST, PORT), daemon=True)
thread_flask.start()

thread_loop = threading.Thread(target=broadcast_mainloop, args=(id_to_room, id_to_client), daemon=True)
thread_loop.start()

# cli
while True:
    cmd = input()
    if cmd in ["exit", "quit", "stop"]:
        
        # disband all rooms
        for room_id in id_to_room:
            id_to_room[room_id].disband()   
        
        sock.close()
        exit(0)
    elif cmd == "clients":
        print(id_to_client)
    elif cmd == "rooms":
        print(id_to_room)
    elif cmd == "help":
        print("\x1b[33mexit\x1b[0m - exit the server")
        print("\x1b[33mclients\x1b[0m - print all currently connected clients")
        print("\x1b[33mrooms\x1b[0m - print all currently open rooms")
    else:
        print("\x1b[2mUnknown command. Type 'help' for a list of commands.\x1b[0m")