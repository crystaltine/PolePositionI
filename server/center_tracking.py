import math
from typing import List
from key_press import Player
#keep track of the center of the track. The only change is in the y position of the center since the entire time the track is moving forward/increasing its x value
#since the track doesn't go in a circle i can just get the center of the track's y position based on the x position of the car.
#this y position is either going to be incremented or decremented based on the turn. if turning left it increases and if turning right it decreases, straight line is constant
#this does mean that i have to hardcode ranges of x values which represent where the turns are. This is for me to increase and decrease y center. 
class Center: 
    def __init__(self):
        #instance variables to keep track of current center x and y
        self.center_x = 0
        self.center_y = 0
        #instance variable to keep track of current range of center values 
        self.center_x_range = None
        #remember to clear the list every time maybe idea for optimization is linked list?
        self.distances = []

        #instance variable that stores the center coordinates as tuples, x position would be the index and that would access the tuple with x and y coordinate
        self.all_center_coordinates = []
        

    #method that will change the y coordinate for center based where the turns are
    def update_center(self, player_x, player_y):
        self.center_x = self.all_center_coordinates(player_x)[0]
        self.center_y = self.all_center_coordinates(player_x)[1]

    #method that calculates the distance from the user to the center of the track
    def distances_to_center(self, player_x, player_y) -> list:
        #clear distances
        self.distances = []
        #if statement to set the range of center values that will be checked, if the user is in the beginning or end, this changes the range that will be checked
        #1000 is an arbitrary value that will eventually be changed to the final x position on the track
        if player_x - 5 >= 0 and player_x + 5 <= 1000:
            self.center_x_range = (player_x - 5, player_x + 5)
        elif player_x - 5 < 0:
            self.center_x_range = (0, player_x + 5)
        else: 
            self.center_x_range = (player_x - 5, 1000)
        lower_x = self.center_x_range[0]
        upper_x = self.center_x_range[1]
        #loop through all of the center_x values and calculate distances the plus 1 is there because I need to loop through the upper value inclusive
        #with how the loop works if the +1 wasnt in the range i would loop through the range excluding the upper_x value 
        for i in range(upper_x - lower_x + 1):
            cx = self.all_center_coordinates(lower_x + i)[0]
            cy = self.all_center_coordinates(lower_x + i)[1]
            dist = math.sqrt((player_x-cx)**2 + (player_y-cy)**2)
            self.distances.add(dist)
        #after this loop distances should be populated with numerous distances with the car to the nearest centers of track

    #method that sees if the user is too far from the track and needs to be blown up
    def too_far(self, player_x, player_y) -> bool:
        #loop through all distances
        for x in self.distances:
            #just looking for one distance that is close enough to account for overshoot
            #50 is an arbitrary number right now that can be adjusted if too generous/limiting
            if x < 50:
                #one distance to center is close enough, can end function and return
                return False
        #if entire loop has gone through and didn't hit the return that means all distances are too far away and True is returned
        return True
    
    #can be changed later but this method gets the distances between all players and then returns list that contains which players crashed and need to be reset 
    #players right now is just a list of player objects
    def collision(self, players: List[Player]):
        for i in range (len(players)):
            for j in range(i+1, len(players)):


#lower = 10 upper = 20, range is 10 