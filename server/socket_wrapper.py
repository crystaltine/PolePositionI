import socket
import json

def _send(socket: socket.socket, data, event_name: str = None) -> None:
    """
    Send wrapper for sockets, adding the prefix data labeler. `data` must 
    be a readable buffer, such as `bytes` or `array.array`.
    """
    if event_name:
        wrapped_data = {
            "type": event_name,
            "data": data
        }
        socket.send(bytes([0]) + bytes(json.dumps(wrapped_data), 'utf-8'))
    
    else:
        socket.send(bytes([1]) + data)