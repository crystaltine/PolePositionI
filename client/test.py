import socket
from time import sleep
from thing import thing
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDP_ADDR = ('127.0.0.1', 3999)

#sock.sendto(bytes('test!', 'UTF-8'), 0, ('127.0.0.1', 3999))
#a, b = sock.recvfrom(1024)
#print(a.decode('UTF-8'))

t = thing()

def send_packet(pos, vel, acc, addr: tuple = None):
    """
    Sends data (JSON-formatted) as packet to server
    """
    addr = addr or UDP_ADDR
    
    buf = struct.pack('%sf' % 3, pos, vel, acc)
    
    sock.sendto(buf, addr)
    

def loop_fps(fps: int, functions: list):
    """
    Runs the given functions in order at `fps` frames per second
    """
    while True:
        a = [function() for function in functions]
        del a
        
        send_packet(t.pos, t.vel, t.acc)
        
        sleep(1/fps)

loop_fps(2, [t.tick, t.display_world])