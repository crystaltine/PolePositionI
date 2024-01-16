import math


class Player:

    def __init__(self):
        self.x = 0 
        self.y = 0
        self.x_velocity = 0 
        self.y_velocity = 0 
        self.x_acceleration = 0 
        self.y_acceleration = 0 
        self.angle_acceleration = 0
        self.angle = 0 
#something to bring up to the team, how will we cover going off the track, will we allow them to go on the grass? what does that mean for my physics calculations?
    #passes in direction of key as well as if it is down or not 
    def num_processing(self, direction: int,  down: bool):
        player1 = Player()
        """
        bool is whether the key is up or down, direction is either a 0, 1, 2, or 3, representing up, down, left, and right respectively 
        should create a player class that stores 6 key numbers, the vertical and horizontal positioning on the map
        for both x and y there has to be a velocity and acceleration 
        i might also need to store an angular veloctiy or some number that relates to how much they're turning 
        """
        #conditional passes if a key is pressed down
        if down:
            #0 and 1 would indicate acceleration forward and backwards
            if direction == 0:
                #corresponding call to the accerlation method to update the speed
                player1.acceleration(True)
            elif direction == 1:
                player1.acceleration(False)
                #right now the method header has a boolean on if the angle change is to be right or not this might be changed but that is why False is passed in since 2 is left
            elif direction == 2:
                player1.set_angle(False)
            else:
                player1.set_angle(True)

            player1.update()
        else:
            #if the key is up and the key pressed was either forwards or backwards, default the acceleration to be something slightly negative to simulate air resistance 
            if direction == 0 or direction == 1:
                self.x_acceleration = -2
            elif direction == 2 or direction == 2:
                self.angle_acceleration = 0

    def set_angle(self, right: bool):
        """
        method based on speed that determines how fast the user is able to turn
        implementation is similar to driving in most games. Don't want to implement losing traction, just limiting how much you can turn based on the velocity of user. 
        lower velocity results in higher angle change per seond vice versa for high
        """
        denominator = 0.1 * self.x_velocity + 2.22 
        self.angle_acceleration = 10/denominator + .5

    
    def acceleration(self, accelerate: bool):
        """
        method that defines how much you accelerate based on your speed, higher speed = lower acceleration and vice versa
        accerlate is a bool that indicates if the person is accerlerating or decelerating
        the equation is different, our acceleration is based on the speed but decelerating will be constant the boolean is used to differentiate between the 2 
        make sure that it's not possible for the velocity to exceed 100
        """
        #setting acceleration based on the boolean and the velocity
        if not accelerate:
            self.x_acceleration = -10
        else:
            self.x_acceleration = math.sqrt(100 - self.velocity)
        
    #have to think about how you change the y as well based on the angle 
    def update(self):
        self.x_velocity += self.x_acceleration
        self.x += self.x_velocity
    
    def get_physics_data(self) -> list:
        """
        Returns a six-element list:
        `[pos_x, pos_y, vel_x, vel_y, acc_x, acc_y]`
        
        Should be sent to client side.
        """
        return [self.x, self.y, self.x_velocity, self.y_velocity, self.x_acceleration, self.y_acceleration]
        
        