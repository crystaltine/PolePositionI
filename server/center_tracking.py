#keep track of the center of the track. The only change is in the y position of the center since the entire time the track is moving forward/increasing its x value
#since the track doesn't go in a circle i can just get the center of the track's y position based on the x position of the car.
#this y position is either going to be incremented or decremented based on the turn. if turning left it increases and if turning right it decreases, straight line is constant
#this does mean that i have to hardcode ranges of x values which represent where the turns are. This is for me to increase and decrease y center. 