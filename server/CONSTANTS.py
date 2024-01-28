TICK_SPEED = 24
TICKS_PER_BROADCAST = 6
HOST, PORT = "localhost", 3999

MAPS = {
    "Touch Grass": {
        "map_name": "Touch Grass",
        "preview_file": "touch_grass.png",
        "length": 3500,
        "world_size": (800, 1000),
        "wr_time": 47.23,
        # TODO - also need to somehow link to a representation of the map, so we can handle physics and stuff.
    } 
}

DRAG_MULTIPLIER = 0.75
""" The amount that velocity is multiplied by every second. """

CAR_COLORS = set(["red", "orange", "yellow", "green", "blue", "purple", "pink", "white"])