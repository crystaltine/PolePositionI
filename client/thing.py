class thing:
    """
    Object with gravity. This is displayed in the terminal, with monospace characters as the units.
    The object display is a line in the terminal. Object falls toward the left and bounces off the left wall.
    Default gravitational acceleration is 2 (monospaces/sec^2)
    Default bounce factor is 0.8 (80% of velocity is retained after bounce)
    """
    
    # Gravitational accel
    G = -0.5
    # Bounce factor
    B = 0.6
    
    def __init__(self):
        self.pos = 100
        self.vel = 0
        self.acc = self.G
        
    def tick(self) -> None:
        """
        Update the object's position and velocity
        """
        self.vel += self.acc
        self.pos += self.vel
        if self.pos <= 0:
            self.pos = 0
            self.vel = -self.vel*self.B
            
    def display_world(self, print_debug = False) -> None:
        """
        Prints a string that represents the world the object is in.
        This is a n-monospace world in the terminal. 
        Empty space is represented by a space, while the ball is represented by a capital 'O'
        Call this 30 times per second to get a smooth terminal animation.
        """
        num_spaces_front = round(self.pos)
        num_spaces_back = round(100 - num_spaces_front - 1)
        print('_'*num_spaces_front + 'O' + '_'*num_spaces_back, end='\r')
        
        if print_debug:
            print(f'pos: {self.pos:.4f}, vel: {self.vel:.4f}, acc: {self.acc:.4f}')