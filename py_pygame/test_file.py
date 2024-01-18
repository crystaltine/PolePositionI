import pygame
import sys
class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        

        self.fillColors = {
            'normal': pygame.Color(255, 255, 255),
            'hover': pygame.Color(190, 190, 190),
            'pressed': pygame.Color(150, 150, 150)
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

        objects.append(self)

    def process(self):

        mousePos = pygame.mouse.get_pos()
        
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])


                if not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

pygame.init()

running = True
   
SKY = (97, 120, 232)
BLACK = (0,0,0)

width = 640
height = 480
objects = []
screen = pygame.display.set_mode([width,height])
screen.fill(SKY)
pygame.display.set_caption("Game")

font = pygame.font.Font('freesansbold.ttf', 32)
grass = pygame.image.load('grasse.png')
grass = pygame.transform.scale(grass, (int(width), int(2 * height/3)))
mtns = pygame.image.load('mtns.png')
mtns = pygame.transform.scale(mtns, (width*2, height/5))


menu_text = font.render('Start playing asp_3', True, BLACK)
menu_rect = menu_text.get_rect(center=(640,260))    #does rect take center as parameter     


        

def print_hello():
    print("hello")
            

def play(): # game screen
#call object instances outside the loop
    while running:
        
        # start_screen(True)
        screen.blit(grass, (0, 2*height/5))
        screen.blit(mtns, (0, height/5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for object in objects:
            object.process()
            
        pygame.display.update()

        #key numbers for keydowbs binary onkeyevent -> send to server
        #up: 00
        #down: 01
        #left: 10
        #right: 11

        #keydown: 1##
        #keyup: 0##


Button(30, 30, 400, 100, 'Button One (onePress)', print_hello)   
play()










