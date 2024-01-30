import pygame
import sys
import math
import socket
import httpx
import json
import threading
from typing import Union, Dict, Callable, Any, TYPE_CHECKING

from CONSTANTS import *
from elements.button import Button
from elements.input import Input
from world.world import World
from map_utils import get_map

from sprite_strip_anim import SpriteStripAnim
import os

# this prevents a circular import
# I NEED TYPE HINTS!!!!!!!!!!!!!!!!!!!!!!
# see - https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from world.entity import Entity

class GameManager:
    """
    A class that declares/scores all assets and resources used, such as screen, buttons, etc.
    
    Implements functions that allow for general display and game management.
    """
    
    game_renderer: Union[None, 'RenderingManager'] = None # of type `renderer.Renderer`
    """ Used for live game. Is `None` until set by `./screens/waiting_room.py` on the `game-init` event. """
    
    # used solely for waiting room event callbacks. See game/screens/waiting_room.py for more info.
    waiting_room_game_started = False
    waiting_room_leave_game = False
    
    # used to determine when to break out of the live game loop
    live_game_proceed_code = 0
    """ 0 is stay, 1 is game ended, 2 is leave game (back to main menu) """
    leaderboard_data = None
    """ Set once game-end event is received. """
    
    # these will be set when we join/create a room
    room_id: Union[None, str] = None
    our_username: str = None
    
    room_details: dict = {
        "map_name": "Touch Grass",
        "preview_file": "touch_grass.png",
        "length": 3500,
        "world_size": (800, 1000),
        "wr_time": 47.23,
    } 
    """ Set after joining/creating a room. Used to store game details. """
    
    # when the unix timestamp is this, begin taking keyboard input and sending to server
    # this gets set when the host starts the game
    start_timestamp: Union[None, float] = None
    
    # Initiate connections with server
    socket_man: 'SocketManager' = None
    http_man: Union[None, 'HTTPManager'] = None
    """ Will be set externally """
    
    # main assets
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    screen.fill(SKY_RGB)

    grass = pygame.image.load('./game/assets/grass.png')
    grass = pygame.transform.scale(grass, (int(WIDTH), int(2 * HEIGHT/3)))
    
    mtns = pygame.image.load('./game/assets/mountains_img.png')
    
    logo_img = pygame.image.load('./game/assets/logo.png')

    car = pygame.image.load('./game/assets/atariPolePosition-carStraight.png')

    # Buttons
    create_game_button = Button(pos=(340,400), display_text="CREATE GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_LARGE)

    join_game_input = Input(x=340, y=480, w=240, h=60, text="")
    join_game_button = Button(pos=(600, 480), display_text="JOIN GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    livegametest_button = Button(pos=(340,560), display_text="LIVEGAMETEST", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)
    quit_button = Button(pos=(600,560), display_text="QUIT", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    countdown_button = Button(pos=(500,150), display_text="READY?", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    # main menu extra text
    text_bottom_left = FONT_TINY.render(MAIN_MENU_BOTTOM_LEFT_TEXT, True, (0, 0, 0))
    text_bottom_right = FONT_TINY.render(MAIN_MENU_BOTTOM_RIGHT_TEXT, True, (0, 0, 0))
    
    @staticmethod
    def get_our_entity() -> 'Entity':
        """
        Returns the entity associated with this client. (finds by username)
        
        Could be None if we aren't in a game
        """
        return GameManager.game_renderer.world.entities[GameManager.our_username]
    
    @staticmethod
    def get_all_other_entities() -> list['Entity']:
        """
        Returns a list of all entities except for our own.
        
        Could be empty if we aren't in a game
        """
        return [v for k,v in GameManager.game_renderer.world.entities.items() if k != GameManager.our_username]
    
        
    @staticmethod
    def draw_road(road_image) -> None:
        GameManager.screen.blit(road_image, (0, -6*RenderingManager.height/5)) 
    
    @staticmethod
    def draw_static_background():
        """
        Draws non-animated grass and mountains on the screen.
        """
        
        GameManager.screen.blit(GameManager.grass, (0, HEIGHT - GameManager.grass.get_height()))
        GameManager.screen.blit(GameManager.mtns, (0, 0))
        
    @staticmethod
    def draw_dynamic_background(angle: int):
        """
        Draws static grass on the screen, but shows different sections of the mountains based on the angle we are turned.
        
        ### How the scrolling works:
        
        - Always render the full height of the mountains
        - When angle is 0, use x=0 -> x=WIDTH as the x range to show.
        - since `mtns_img` is 4320x300px, 1 degree is 4320/360 = 12px
        
        Thus, the x-coord of the left side should be `angle * 12`, and the right side should be `angle * 12 + WIDTH`
        """
        
        angle = int(angle % 360)
        crop_pos_on_img = angle*12, 0
        size_of_crop = WIDTH, HEIGHT - GameManager.grass.get_height()
        
        GameManager.screen.blit(GameManager.mtns, (0, 0), (*crop_pos_on_img, *size_of_crop))
        
        if angle > 360-math.degrees(FOV):
            # we ran past the right side of the png.
            # so, in addition to the x=0 blit, we need to do an x= 12*(360-angle) blit
            # we can actually omit the size, since it can just overflow off the screen
            GameManager.screen.blit(GameManager.mtns, (12*(360-angle), 0))        
            
        # and then always draw the grass
        GameManager.screen.blit(GameManager.grass, (0, HEIGHT - GameManager.grass.get_height()))
        
    @staticmethod
    def draw_logo(posx = 200, posy = 50, scale = 1):
        """
        Draws the logo on the screen, with customizable position and scale. posx and posy are the top left corner of the logo.
        
        For reference, the original logo is 800x300 pixels.
        """
        scaled_logo = GameManager.logo_img
        if scale != 1:
            scaled_logo = pygame.transform.scale(scaled_logo, (int(scaled_logo.get_width() * scale), int(scaled_logo.get_height() * scale)))
        
        GameManager.screen.blit(scaled_logo, (posx, posy))
        
    @staticmethod
    def draw_homescreen_text():
        GameManager.screen.blit(GameManager.text_bottom_left, (20, HEIGHT - FONT_SIZES["tiny"] - 20))
        GameManager.screen.blit(GameManager.text_bottom_right, (WIDTH - GameManager.text_bottom_right.get_width() - 20, HEIGHT - FONT_SIZES["tiny"] - 20))
     
    @staticmethod   
    def TitleScreen():
        """
        Draws the title screen background, logo, and text.
        """
        GameManager.draw_static_background()
        GameManager.draw_homescreen_text()
        GameManager.draw_logo()
    
    @staticmethod  
    def loop_titlescreen_buttons():
        """
        Handles styling and hovering on main menu buttons/inputs. Run inside the game loop.
        Doesn't do anything about clicks - that's handled in the `main_menu` function.
        
        Affected elements:
        - create_game_button
        - join_game_input
        - join_game_button
        - livegametest_button
        - quit_button
        """
        GameManager.create_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.create_game_button.update(GameManager.screen)
        
        GameManager.join_game_input.draw(GameManager.screen)
        
        GameManager.join_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.join_game_button.update(GameManager.screen)
        
        GameManager.livegametest_button.changeColor(pygame.mouse.get_pos())
        GameManager.livegametest_button.update(GameManager.screen)
        
        GameManager.quit_button.changeColor(pygame.mouse.get_pos())
        GameManager.quit_button.update(GameManager.screen)
    
    @staticmethod 
    def loop_countdown_button():
        GameManager.countdown_button.update(GameManager.screen)

    @staticmethod 
    def draw_car(sideways_pos:int):
        """
        Draws the car in the bottom-ish center of the screen (centered x, 80% y)
        """
        GameManager.screen.blit(c:=GameManager.car, ((WIDTH/2 - c.get_width()/2) - sideways_pos * 4, 4*HEIGHT/5 - c.get_height()/2))
    
    @staticmethod 
    def quit_game():
        """
        Exits the game gracefully.
        """
        print(f"\x1b[35Quitting the game gracefully...\x1b[0m")
        
        # leave the room if we are in one
        if GameManager.room_id is not None:
            GameManager.http_man.leave_room()
            
        # close the socket connection
        if hasattr(s:=GameManager.socket_man, 'socket'): 
            s.stop_listening()
            s.socket.close()
        
        pygame.quit()
        sys.exit()
        
class RenderingManager:
    """
    Handles all rendering of the live game, as well as all updates to the internal physics engine
    based on the data the server sends us (every minute)
    
    We keep an internal physics engine for smoother animations, although server data overrides this.
    
    @TODO - we should probably destroy this object when the game ends (once we implement game end logic)
    """

    width = 1200 #2.4
    height = 720 #1.6

    road_straight = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\straight road'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
    curved_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved left'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
    curved_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\curved right'), (0, -3*height/5, width, 4*height/3), 12, -1, True, 0.041)
    left_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\left centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.08)
    right_centering = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\right centering'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.125)
    turning_left = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning left'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.041)
    turning_right = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets\\road frames\\turning right'), (0, -3*height/5, width, 4*height/3), 8, -1, False, 0.125)

    #all linked animations for the full track
    roadpaths = [
        road_straight, 
        turning_left,
        curved_left, 
        left_centering,
        road_straight, 
        turning_right,
        curved_right,
        right_centering,
        road_straight,
        turning_left,
        curved_left, 
        left_centering,
        road_straight,
        turning_right,
        curved_right,
        right_centering,
        road_straight,
        turning_left,
        curved_left, 
        left_centering,
        road_straight
    ]
    roadpaths_index = 0

    
    def __init__(self, init_entities: list = []) -> None:
        """
        Creates a `RenderingManager` to run internal physics.
        
        Map name comes from `GameManager`.
        
        `init_entities` should be an (optional) list of entities, each of which is a dict of the format:
        ```typescript
        {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number
            }
        }
        """
        
        map_class = get_map(GameManager.room_details['map_name'])
        self.world = World(map_class.world_size, map_class.track_geometry)
        
        for entity in init_entities:
            self.place_entity(entity)

    @staticmethod
    def render_frame(road_moving:bool):
        """
        Draws on the screen a single frame based on the current state of the internal physics engine.
        """
        
        GameManager.draw_dynamic_background(GameManager.get_our_entity().angle%360)

        #add road
        #RenderingManager.roadpaths[RenderingManager.roadpaths_index].iter()
        if road_moving:
            road_image = RenderingManager.roadpaths[RenderingManager.roadpaths_index].current()
            road_image = pygame.transform.scale_by(road_image, (2.4, 1.82))      
            GameManager.draw_road(road_image) 
            #pygame.display.update()
            road_image = RenderingManager.roadpaths[RenderingManager.roadpaths_index].next()
            if road_image is None:
                roadpaths_index += 1
                RenderingManager.roadpaths[roadpaths_index].iter()
                road_image = RenderingManager.roadpaths[RenderingManager.roadpaths_index].current()
            road_image = pygame.transform.scale_by(road_image, (2.4, 1.82))
        else:
            road_image = RenderingManager.roadpaths[RenderingManager.roadpaths_index].current()
            road_image = pygame.transform.scale_by(road_image, (2.4, 1.82))      
            GameManager.draw_road(road_image) 
        
        # For each other entity, draw on screen
        
        sorted_by_dist = sorted(GameManager.get_all_other_entities(), key=lambda e: e.pos[0]**2 + e.pos[1]**2, reverse=True)
        
        for other in sorted_by_dist:
            size = RenderingManager.get_rendered_size(other)
            pos = (WIDTH/2 + RenderingManager.angle_offset(other), RenderingManager.get_y_pos(other))
            RenderingManager.draw_entity(size, pos, other.color)
            
        GameManager.draw_car(GameManager.get_our_entity().pos[1]) # draw our own car on top of everything else

        # pygame.display.update()
        
    def tick_world(self):
        """
        Updates the internal physics engine by one tick
        
        This depends on the FPS of the client-side game. 24/s at the time of writing
        """
        
        self.world.update()
    
    def place_entity(self, entity_data: dict) -> bool:
        """
        `entity_data` must be of the format:
        ```typescript
        {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number
            }
        }
        ```
        
        Adds the entity to the world.
        This should be used on the first physics data packet (or some special init packet once a game starts)
        
        Returns `True` if the entity is new (checked based on username) and was added, `False` if it already exists
        """
        
        if entity_data['username'] in self.world.entities:
            return False
        
        self.world.create_entity(
            entity_data['username'],
            entity_data['color'],
            **entity_data['physics']
        )
        
        # update world
        self.tick_world()
     
    def set_physics(self, data: list):
        """
        Updates the internal physics engine with the data the server sends us.
        
        This depends on the broadcast frequency of the server. 1/s at the time of writing
        
        `data` should have the same schema as the `World.get_all_data` function, which looks like this:
        ```typescript
        [
          {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: [vel_x: number, vel_y: number],
              acc: [acc_x: number, acc_y: number],
              angle: number,
              hitbox_radius: number,
              keys: [bool, bool, bool, bool]
            }
          },
          ...
        ]
        ```
        
        (each one of those objects is an entity)
        """
        
        # for each object in that list, update the corresponding entity.
        for entity_data in data:
            self.world.entities[entity_data['username']].set_physics(entity_data['physics'])
            
    @staticmethod
    def get_rendered_size(other: 'Entity') -> int:
        """
        ### See `../RENDERER_NOTES.png`
        
        Returns a size in px for the eneity based on how far away and at what angle it is from us.
        """
        
        us = GameManager.get_our_entity()
        
        dist = math.sqrt((other.pos[0] - us.pos[0])**2 + (other.pos[1] - us.pos[1])**2)
        theta = (math.asin(other.hitbox_radius / (dist + other.hitbox_radius)))
        width_on_screen = (WIDTH/2) * 2*theta/(FOV/2) # 2 and 4 are static (do not adjust)
        
        # print(f"\x1b[34mget_rendered_size\x1b[0m: dist={dist}, theta={theta} size={width_on_screen}")
        return round(width_on_screen)
        
    @staticmethod
    def get_y_pos(other: 'Entity') -> int:
        """
        Returns a y-position on the screen based on an entity's distance from us.
        
        The idea is that farther away entities should be drawn higher up (lower y-value)
        because they are closer to the horizon.
        
        Will not return a value lower than 300 (the horizon)
        and higher than 600 (bottom of screen, with some padding ofc)
        
        ### The function used for this calculation
        (can be changed - i just picked a random asymptotic decay from 600->300 in desmos)
        
        y_coord = `30000/(dist+100) + 300`
        """    
        
        us = GameManager.get_our_entity()
        
        dist = math.sqrt((other.pos[0] - us.pos[0])**2 + (other.pos[1] - us.pos[1])**2)
        return round(30000/(2*dist+100) + 300)
        
    @staticmethod
    def angle_offset(other: 'Entity') -> Union[int, None]:
        """
        ### See `../RENDERER_NOTES.png`
        
        Returns how many pixels relative to the center of the screen we should draw CENTER of the other entity at,
        based on the angle between us and the other entity.
        """
        
        us = GameManager.get_our_entity()
        
        theta = math.atan2(other.pos[1] - us.pos[1], other.pos[0] - us.pos[0]) - math.radians(us.angle%360)
        theta = RenderingManager.adjust_angle(theta) # clamp to 0-360
        D = int((theta/(FOV/2)) * (WIDTH/2))
        
        # print(f"\x1b[34mangle_offset\x1b[0m: theta={theta}, offset={D}")
        
        return D
    
    @staticmethod
    def adjust_angle(radians: float) -> float:
        """
        Adjusts an angle to a -pi -> pi range. Returns in RADIANS.
        """
            
        return radians % (2*math.pi) - math.pi
    
    @staticmethod
    def draw_entity(size: int, pos: tuple[int, int], color: str) -> None:
        """
        Draws an entity on the screen, given a size, offset, and color.
        
        Currently, all it draws is a circle. (TODO - implement 3d models/rotating sprites)
        """
        
        # print(f"Drawing entity at {pos} with size {size} and color {color}")
        pygame.draw.circle(GameManager.screen, color, pos, size)
        
class SocketManager:
    """
    Handles all the client-server socket-tick processes, including:
    - Listening for movement key presses
    - Sending packets to server containing that key data
    - Listening for physics data from server side
    """
    
    def __init__(self):
        """
        Simply creates a pointer to this future object.
        
        Also initializes a few basic things
        """
    
        self._listen_stopped = True
        self.registered_events: Dict[str, Callable[[Dict], Any]] = {}
        """ Should be a dict mapping event names to callback functions. """
        
        return
    
    def connect(self, username: str) -> Union[str, None]:
        """
        Creates a socket connection with the server. **Because this contains `socket.recv` calls, it WILL BLOCK THE MAIN THREAD.**
        
        Returns None if connection failed, else returns the client id.
        
        This function also begins the listening thread.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SOCKET_HOST, SOCKET_PORT))
            
            # IMPORTANT: see server/server.py: we need to send the server a username immediately
            self.socket.send(username.encode('utf-8'))
            
            # Receive client id - special event that is sent on connection
            res = self.socket.recv(1024)
            self.client_id = res.decode('utf-8')
            
            self.listen() # now we begin listening for the general format
            
            return self.client_id
        except Exception as e:
            print(f"\x1b[31mError connecting to server: {e}\x1b[0m")
            return None

    def listen(self) -> None:
        """
        Starts a thread that purely listens for messages from the server.
        Since this runs on a different thread, it will not block the main thread.
        
        The main purpose of this is to listen for events such as:
        - game-init (when we should proceed to live game screen/begin countdown)
        - game-start (when we actually start moving, which should be a bit delayed due to countdown/loading times)
        - crash (our car crashed, start respawn screen)
        - player-left (when player leaves lobby, and we have to rerender it)
        """
        
        self._listen_stopped = False
        
        def listen_inner():
            try:
                while True:
                    
                    if self._listen_stopped: break

                    raw_data = self.socket.recv(1024)
                    payload = json.loads(raw_data[1:].decode('utf-8'))
                    
                    # prefixing: first byte will be a '0' for events, '1' for packet data
                    if raw_data[0] == 1: 
                        self.on_packet(payload)
                        continue

                    event_name = payload.get('type')
                    data = payload.get('data')
                    
                    _callable = self.registered_events.get(event_name)
                    if not (_callable is None): 
                        print(f"\x1b[35mHandling Event \x1b[33m{event_name}\x1b[0m")
                        _callable(data)
                    else:
                        print(f"\x1b[2mIgnoring Unhandled event \x1b[0m\x1b[33m{event_name}\x1b[0m")
            except (ConnectionAbortedError, ConnectionResetError) as e:
                print(f"\x1b[31mConnection to server disrupted!\x1b[0m")
                        
        self.listen_thread = threading.Thread(target=listen_inner)
        self.listen_thread.start()
    
    def stop_listening(self) -> None:
        """
        Stops the listening thread. Registered events stay, but won't be called until `listen()` is called again.
        """
        self._listen_stopped = True
    
    def on_packet(self, world_data: list) -> None:
        """       
        Handles a received physics packet from the server.
        
        The data should tell us the physics of every entity in the world. It has the following schema:
        ```typescript
        [
          {
            username: string,
            color: string,
            physics: {
              pos: [number, number],
              vel: [number, number],
              acc: [number, number],
              angle: number,
              hitbox_radius: number,
              keys: [bool, bool, bool, bool]
            }
          },
          ...
        ]
        ```
        """
        
        print(f"\x1b[35mPACKET RECV: \x1b[33m{len(world_data)}\x1b[0m playerdata packets included")
        GameManager.game_renderer.set_physics(world_data)
                
    def on(self, event_name, callback: Callable[[Dict], Any]) -> None:
        """
        Registers a callback function to be called when the specified event is received from the server.
        
        If the event is already registered, this will overwrite the previous callback.
        
        ### Warning: Event handlers run on the listening thread. Do not use blocking functions.
        
        @param `event_name`: the name of the event to listen for
        @param `callback`: the function to call when the event is received. The callback function should accept one parameter, which will be JSON-formatted data from server.
        """
        
        self.registered_events[event_name] = callback        

    def handle_game_keypresses(self, event) -> None:
        """
        ### Must run INSIDE a `for event in pygame.event.get()` loop.
        
        This function listens for the following keys:
        - W, A, S, D
        - Up, Down, Left, Right arrows
        
        On keyDown or keyUp event, prepares a packet to upload to server
        
        ### Packet encoding table:
        
        #### Leftmost bit: 1=keydown, 0=keyup
        
        #### Bits 2 and 3: 00=forward, 01=backward, 10=left, 11=right
        
        - `000` - forward keyup
        - `001` - backward keyup
        - `010` - left keyup
        - `011` - right keyup
        - `100` - forward keydown
        - `101` - backward keydown
        - `110` - left keydown
        - `111` - right keydown
        """
        
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keyid = id_map.get(event.key)
            if keyid is None: return
            
            # Also update our physics on the client side, so that its more smooth
            us = GameManager.get_our_entity()
            us.key_presses[keyid] = event.type == pygame.KEYDOWN
            
            keydown = event.type == pygame.KEYDOWN
            self.send_packet(keyid, keydown)

    def send_packet(self, keyid: int, keydown: bool) -> None:
        """
        Creates and sends a keyinfo packet to the server.
        Each packet should have a payload size of 3 bits.
        """
        keydata = keyid | (keydown << 2)
        print(f"Creating&sending packet with keyid={keyid}, keydown={keydown}")
        self.socket.send(keydata.to_bytes(1, 'big'))
    
class HTTPManager:
    """
    ### Initialize after SocketManager instance is created and client id is obtained.
    
    Contains functions that handle all client-side services that have to do with HTTP requests, 
    such as creating rooms, joining rooms, receiving scores, etc.
    """
    
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
    
    def create_room(self) -> dict:
        """
        Uses the client id obtained from initalization to create a room.
        If the request is successful, the client will be automatically added to the room.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "code": Union[str, None], # will be a 6-digit code if successful
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        room_data = HTTPManager.api_call(f"/createroom/{self.client_id}")
        print(f"Create room response: {room_data}")
        return room_data

    def join_room(self, room_id: str) -> dict:
        """
        Sends a join room request to the server.
        Provide a room id from an input field that the user types in.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        
        if not room_id.isalnum():
            return {"success": False, "message": "Room code must be alphanumeric."}
        
        res = HTTPManager.api_call(f"/joinroom/{self.client_id}/{room_id}")
        print(f"Join room response: {res}")
        return res

    def start_game(self, room_id: str) -> dict:
        """
        Call this function once the user has created their own room and is ready to start.
        
        Requires id passed in as param because I want to avoid circular imports.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        res = HTTPManager.api_call(f"/startgame/{self.client_id}/{room_id}")
        print(f"Start game response: {res}")
        return res
    
    def leave_room(self) -> dict:
        """
        Call this function when the user is ready to leave the room.
        
        Returns a JSON/`dict` with the following schema:
        ```
        {
            "success": bool,
            "message": Union[str, None] # will be an error message if unsuccessful
        }
        ```
        """
        res = HTTPManager.api_call(f"/leaveroom/{self.client_id}")
        print(f"Leave room response: {res}")
        return res
    
    @staticmethod
    def api_call(endpoint: str, query_params: dict = None) -> dict:
        """
        (internal) Makes a GET request to the server.
        
        @param endpoint: the endpoint to call, e.g. `createroom` (no leading slash)
        @param query_params: a `dict` of query parameters to pass to the endpoint.
        
        @returns: a JSON/`dict` containing the response data
        """
        
        query_params_string = ""
        if query_params:
            query_params_string = "?" + "&".join([f"{key}={val}" for key, val in query_params.items()])
        try:
            res = httpx.get(f"{HTTP_URL}/{endpoint}{query_params_string}")
            return res.json()
        except Exception as e:
            print(f"\x1b[31mError making API call: {e}\x1b[0m")
            return {"success": False, "message": f"Couldn't connect to the server."}
        
def init_managers():
    """
    Run on game start
    """
    GameManager.socket_man = SocketManager()