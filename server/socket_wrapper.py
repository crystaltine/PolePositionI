import socket
import json

def _send(socket: socket.socket, data, event_name: str = None) -> bool:
    """
    Send wrapper for sockets, adding the prefix data labeler. `data` must 
    be a readable buffer, such as `bytes` or `array.array`.
    
    Please send `data` as a string (since we must serialize it to JSON)
    
    Returns `true` if the data was sent successfully, `false` otherwise.
    """
    try:
        if event_name:
            wrapped_data = {
                "type": event_name,
                "data": data
            }
            socket.send(bytes([0]) + bytes(json.dumps(wrapped_data), 'utf-8'))
        
        else:
            socket.send(bytes([1]) + data)
            
        return True
    except (ConnectionResetError, ConnectionAbortedError):
        print(f"\x1b[31mCould not send (event=\x1b[33m{event_name}\x1b[0m) to socket: Connection closed!\x1b[0m")
        return False