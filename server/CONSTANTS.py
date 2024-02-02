TICK_SPEED = 24
TICKS_PER_BROADCAST = 6
HOST, PORT = "localhost", 3999

MAPS = {
    "Touch Grass": {
        "map_name": "Touch Grass",
        "map_file": "TouchGrass.map",
        "preview_file": "touch_grass.png",
        "backdrop_file": "TouchGrass.png",
        "length": 3500,
        "width": 100,
        "oob_leniency": 10,
    },
    "Curvy": {
        "map_name": "Curvy",
        "map_file": "Curvy.map",
        "preview_file": "curvy.png",
        "backdrop_file": "Curvy.png",
        "length": 5000,
        "width": 120,
        "oob_leniency": 5,
    } 
}

TRACK_WIDTH = 100
""" Total horizontal width of the track. This relates to the `y` position variable of Entities (`Entity.pos[1]`) """
OOB_LENIENCY = 10
""" How far off the track a car can go before it is considered out of bounds. """

CRASH_DURATION = 5
""" Penalty in seconds for crashing. """

CAR_COLORS = set(["red", "orange", "yellow", "green", "blue", "purple", "pink", "white"])