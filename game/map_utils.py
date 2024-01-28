from maps.touch_grass import TouchGrass

def get_map(map_name: str):
    """
    Returns a map object based on the map name, since the server sends us a map name only.
    
    The client side must store the geometry of the map. (MUST MATCH SERVER!)
    """
    
    match map_name:
        case "Touch Grass":
            return TouchGrass
        case _:
            raise ValueError(f"Map name {map_name} not found in maps list!")