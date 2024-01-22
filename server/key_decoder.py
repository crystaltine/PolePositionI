keymap = ["forward", "backward", "left", "right"]

def decode_packet(data: int) -> tuple:
    """
    Decodes a packet (single `int` in `[0, 7]`) received from client into [keyname: str, keydown: bool]

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
    
    ### Returns:
    `tuple(keyid: int, keydown: bool)`
    """
    keyid = data % 4
    keydown = data >> 2

    return (keyid, bool(keydown))