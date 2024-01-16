import math


class Player:

    def __init__(self):
        self.x = 0 
        self.y = 0
        self.velocity = 0
        self.acceleration = 0
        self.x_velocity = 0 
        self.y_velocity = 0 
        self.x_acceleration = 0 
        self.y_acceleration = 0 
        self.angle_acceleration = 0
        self.angle = 0 
        self.up = None
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
                player1.accelerate(True)
            elif direction == 1:
                player1.accelerate(False)
                #right now the method header has a boolean on if the angle change is to be right or not this might be changed but that is why False is passed in since 2 is left
            elif direction == 2:
                player1.set_angle()
                player1.up = True
            else:
                player1.set_angle()
                player1.up = False
        else:
            #if the key is up and the key pressed was either forwards or backwards, default the acceleration to be something slightly negative to simulate air resistance 
            if direction == 0 or direction == 1:
                self.x_accerlation = -2
            elif direction == 2 or direction == 3:
                self.angle_acceleration = 0
        player1.update()
        


    # use sin and cos to get the x and y velocity 
    #in the update also have to change the x and y acceleration by using the sin and cos 
    #if right is true that means they are going down and vice versa for False 
    def set_angle(self):
        """
        method based on speed that determines how fast the user is able to turn
        implementation is similar to driving in most games. Don't want to implement losing traction, just limiting how much you can turn based on the velocity of user. 
        lower velocity results in higher angle change per seond vice versa for high
        """
        denominator = 0.1 * self.x_velocity + 2.22 
        self.angle_acceleration = 10/denominator + .5

    
    def accelerate(self, accelerate: bool):
        """
        method that defines how much you accelerate based on your speed, higher speed = lower acceleration and vice versa
        accerlate is a bool that indicates if the person is accerlerating or decelerating
        the equation is different, our acceleration is based on the speed but decelerating will be constant the boolean is used to differentiate between the 2 
        make sure that it's not possible for the velocity to exceed 100
        """
        #setting acceleration based on the boolean and the velocity
        if not accelerate:
            self.acceleration = -10
        else:
            self.acceleration = math.sqrt(100 - self.velocity)
        
    #update function that is called numerous times a second to update the car's position, velocities, and accelerations
    #this has to be changed based on where the car is on the position. When driving in a indy 500 esque track, after taking the first turn the car is now pointed in the opposite
    #direction and the velocity should subtract from the x position 
    #solutions to this is either with our partitioning of the track into many rectangles which was already going to be used with our tracking of if the car is on the track
    #this would then be used to see if the x_velocity should add or subtract to the x position 

    #update, our track will most likely not go in a circle but if it does, keep this in mind 
    def update(self):
        # self.x_velocity += self.x_acceleration
        # self.x += self.x_velocity
        #set overall velocity by adding the acceleration
        self.velocity += self.acceleration
        #self.up is a boolean instance variable used to check if the car is at any angle other than completely straight might have to change later
        #If the car is at an angle, up is not None
        if self.up is not None:
            #have to set angle and x velocity 
            self.angle = math.abs(self.angle + self.angle_acceleration)
            self.x_velocity = self.velocity * math.cos(self.angle)
            if self.up:
                self.y_velocity += self.velocity * math.sin(self.angle)
            else:
                self.y_velocity -= self.velocity * math.sin(self.angle)
        self.x += self.x_velocity
        self.y += self.y_velocity 
    
    def get_physics_data(self) -> list:
        """
        Returns a six-element list:
        `[pos_x, pos_y, vel_x, vel_y, acc_x, acc_y]`
        
        Should be sent to client side.
        """
        return [self.x, self.y, self.x_velocity, self.y_velocity, self.x_acceleration, self.y_acceleration]
        
        