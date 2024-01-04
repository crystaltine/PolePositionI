keymap = ["forward", "backward", "left", "right"]

def decode_packet(data: int) -> str:
    """
    Decodes a packet received from client into [keyname: str, keydown: bool]
    ### For now, however, just print a debug

    ### Packet encoding table:
     
    #### Leftmost bit: 1=keydown, 0=keyup
    
    #### Bits 2 and 3: 00=forward, 01=backward, 10=left, 11=right
    
    - `000` - forward keyup
    - `001` - backward keyup
    - `010` - left keyup
    - `011` - right keyup
    - `100` - forward keydown
    - `101` - backward keydown
    - `110` - left keydown
    - `111` - right keydown

    Example: 3 = 011 = right keyup
    """
    keyid = data % 4
    keydown = data // 4

    return (keyid, keydown)