from socket import socket
import json

class PSocket(socket):
    """
    A Prefix wrapper for the python socket class.
    
    The only change this wrapper makes is that the send function adds an extra parameter "type", which should be either an event name, or None.
    If event is provided, this socket adds a prefix byte of 0 to the data before sending. If not, it adds a prefix byte of 1 (a packet)
    """
    def __init__(self, socket: socket):
        self.socket = socket
        
    def send(self, data: bytes, event_name: str = None) -> None:
        """
        Sends data to the socket.
        
        @param `data`: the raw JSON data to send. this function will handle wrapping it into a {event, data} object.
        @param `event_name`: the name of the event to be sent to the client. Leave none for packet (no event). This should be the same as the event name used in the `SocketManager.on()` registration on the client side.
        """
        
        if event_name:
            wrapped_data = {
                "type": event_name,
                "data": data
            }
            self.socket.send(bytes([0]) + bytes(json.dumps(wrapped_data), 'utf-8'))
        
        else:
            self.socket.send(bytes([1]) + data)
            
    def send_raw(self, data: bytes) -> None:
        """
        Sends raw data to the socket, without prefixing.
        
        Basically the same as the original socket.send() function.
        """
        self.socket.send(data)