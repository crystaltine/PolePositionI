from socket import socket

from key_press import Player

class Room:
    def __init__(self, clients: list, id: int):
        self.clients = set(clients)
        self.id = id

    def add_client(self, client):
        self.clients.add(client)

    def broadcast_all(self, sock: socket, data):
        print(f"\x1b[35mbroadcast_all:\x1b[0m data={data}")
        for client in self.clients:
            if client.address:
                sock.sendto(data, client.address)
            else:
                print(f"Room {id}: \x1b[31mUnable to send data to unaddressed client\x1b[0m")


class Client:
    """
    Contains all information related to a connected socket
    
    This can include:
    - `address` (tuple(host, port))
    - The `id` that was generated on the client-side (reverse cookie-like)
    - The ID of the room they are currently connected to
    - A `key_press.Player` object that stores data about the player, like pos, vel, and acc
    """
    def __init__(self, sock, host: str = None, port: int = None, id: str = None, room: int = None):
        self.sock = sock
        self.address = (host, port)
        self.id = id
        self.room = room
        self.player = Player()

    def update_player(self):
        self.player.update()

    def update_player_keys(self, keyID: int, down: bool):
        """
        Updates player data with new keypress data received from them
        """
        self.player.num_processing(keyID, down)
        print(f"\x1b[35mPLAYER UPDATING! keyID={keyID}, down={down}")
        
    def __str__(self) -> str:
        return f"(Client addr=\x1b[33m{self.address}\x1b[0m, id=\x1b[33m{self.id}\x1b[0m), room=\x1b[33m{self.room}\x1b[0m)"
    