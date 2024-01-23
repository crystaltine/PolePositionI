#keep track of the center of the track. The only change is in the y position of the center since the entire time the track is moving forward/increasing its x value
#since the track doesn't go in a circle i can just get the center of the track's y position based on the x position of the car.
#this y position is either going to be incremented or decremented based on the turn. if turning left it increases and if turning right it decreases, straight line is constant
#this does mean that i have to hardcode ranges of x values which represent where the turns are. This is for me to increase and decrease y center. 
class Center: 
    def __init__(self):
        self.center_x = 0
        self.center_y = 0
    
    #method that will change the y coordinate for center based where the turns are
    def update_center(self, player_x, player_y):
        pass

    #method that calculates the distance from the user to the center of the track
    def distances_to_center(self, player_x, player_y) -> list:
        #if statement to set the range of center values that will be checked, if the user is in the beginning or end, this changes the range that will be checked
        if player_x - 5 >= 0 and player_x + 5 <= 1000:
            center_x_range = (player_x - 5, player_x + 5)
        elif 
    #method that sees if the user is too far from the track and needs to be blown up
    def too_far(self, player_x, player_y) -> bool:
        pass
