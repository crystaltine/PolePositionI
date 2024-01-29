import math
from typing import List
from key_press import Player
import center_tracking


#method that will scale the sizes of nearby players based on distance from current player 
def distance_scale(current_player: Player, players: List[Player]):
    to_be_rendered = []
    #populates to_be_rendered with the player objects that are close enough and in front of the current player's car 
    for i in players:
        dist = center_tracking.distance(current_player.x, current_player.y, i.x, i.y)
        #if the other cars are close enough and they are in front of the player
        if dist < 500 and i.x > current_player.x:
            to_be_rendered.append(i)
    