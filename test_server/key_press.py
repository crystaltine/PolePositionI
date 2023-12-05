import math 
class Player:
    self.x
    self.y
    self.velocity
    self.acceleration
    self.angle


#something to bring up to the team, how will we cover going off the track, will we allow them to go on the grass? what does that mean for my physics calculations?
    def num_processing(direction: int,  down: bool):
        """
        bool is whether the key is up or down, direction is either a 0, 1, 2, or 3, representing up, down, left, and right respectively 
        should create a player class that stores 6 key numbers, the vertical and horizontal positioning on the map
        for both x and y there has to be a velocity and acceleration 
        i might also need to store an angular veloctiy or some number that relates to how much they're turning 
        """
        #use while loop that runs 24 times a second to have the vehicle constantly accelerating or decelerating 
        pass


    def angular_acceleration():
        """
        method based on speed that determines how fast the user is able to turn
        implementation is similar to driving in most games. Don't want to implement losing traction, just limiting how much you can turn based on the velocity of user. 
        lower velocity results in higher angle change per seond vice versa for high
        """
        pass

    
    def acceleration(accelerate: bool):
        """
        method that defines how much you accelerate based on your speed, higher speed = lower acceleration and vice versa
        accerlate is a bool that indicates if the person is accerlerating or decelerating
        the equation is different, our acceleration is based on the speed but decelerating will be constant the boolean is used to differentiate between the 2 
        make sure that it's not possible for the velocity to exceed 100
        """
        if not accelerate:
            self.acceleration = -10
        else:
            self.accerlation = math.sqrt(100 - self.velocity)