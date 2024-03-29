import pygame
import sys
import math
import socket
import httpx
import json
import threading
import os
from time import time_ns
from typing import Union, Dict, List, Callable, Any, TYPE_CHECKING
from tkinter import *
from tkinter import messagebox, simpledialog

from CONSTANTS import *
from animator import RoadAnimator, SpriteStripAnim
from elements.button import Button
from elements.input import Input
from world.world import World

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
    
    tk_root = Tk()
    tk_root.withdraw()
    
    game_renderer: 'RenderingManager' = None # of type `renderer.Renderer`
    #: Union[None, 'RenderingManager']
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
    room_id = None
    #removed type hint - : Union[None, str]
    our_username: str = None
    
    map_data: dict = None
    """
    Set after joining/creating a room. Format:
    ```typescript
    {
      map_name: string,
      map_file: string, // the file inside ./maps, on both the server and client
      preview_file: string, // the file the client should load as a waiting room preview img
      length: number,
      width: number,
      oob_leniency: number,
    } 
    ```
    """
    
    crash_end_timestamp = 0
    """ Determines when our crash respawn timer ends. Set when we crash. """
    
    # when the unix timestamp is this, begin taking keyboard input and sending to server
    # this gets set when the host starts the game
    start_timestamp = None
    #: Union[None, float]
    
    # Initiate connections with server
    socket_man: 'SocketManager' = None
    http_man = None
    #: Union[None, 'HTTPManager']
    """ Will be set externally """
    
    accumulated_angle: float = 0.0
    """
    Used to determine how to scroll mountains. Gets changed at a rate of `track_angle * ANGLE_ACCUMULATION_FACTOR` per second.
    """
    
    last_y_pos: float = 0
    """
    Used to determine where to draw the explosion (horizontally) on the crash event, since the event sets y-pos back to 0.
    """
    
    # main assets
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    pygame.display.set_caption("Pole Position I")
    screen.fill(SKY_RGB)

    grass = pygame.image.load('./game/assets/grass.png')
    grass = pygame.transform.scale(grass, (int(WIDTH), int(2 * HEIGHT/3)))
    
    backdrop = pygame.image.load(f'./game/assets/backdrops/Default.png')
    def set_backdrop(map_name: str) -> None:
        """
        Sets the backdrop image based on the map name.
        The map name should be `PascalCase` (e.g. `Curvy`, `TouchGrass`)
        """
        GameManager.backdrop = pygame.image.load(f'./game/assets/backdrops/{map_name}')
    
    logo_img = pygame.image.load('./game/assets/logo.png')

    
    car = None
    """This will be set once we join/create a room and obtain a car color."""

    #animted explosion
    boom = SpriteStripAnim(os.path.join(os.path.dirname(__file__), 'assets/explosion'), (0, 0, WIDTH, HEIGHT), 5, -1, True, 0.25)

    progressbar_img = pygame.image.load('./game/assets/progress_bar_frame.png')

    # Buttons
    create_game_button = Button(pos=(340,400), display_text="CREATE GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_LARGE)

    join_game_input = Input(x=340, y=480, w=240, h=60, text="")
    join_game_button = Button(pos=(600, 480), display_text="JOIN GAME", base_color="#ffffff", hovering_color="#96faff", image=BUTTON_MEDIUM)

    quit_button = Button(pos=(340,560), display_text="QUIT", base_color="#ffffff", hovering_color="#ff9696", image=BUTTON_LARGE)
    
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
    def reset() -> None:
        """
        Resets variables used for game lifecycle, to be avaiable for new games.
        """
        GameManager.waiting_room_game_started = False
        GameManager.waiting_room_leave_game = False
        GameManager.live_game_proceed_code = 0
        GameManager.start_timestamp = None
        GameManager.accumulated_angle = 0.0
        GameManager.room_id = None
        GameManager.last_y_pos = 0
        
    @staticmethod
    def draw_road(road_image) -> None:
        """
        Draws the road image on screen.
        
        The road sprite should be HEIGHT-240px tall, and span the whole width.
        
        Thus, it it blitted at (0, 240)
        """
        GameManager.screen.blit(road_image, (0, 240))
    
    @staticmethod
    def draw_static_background():
        """
        Draws non-animated grass and mountains on the screen.
        """
        
        GameManager.screen.blit(GameManager.grass, (0, HEIGHT - GameManager.grass.get_height()))
        GameManager.screen.blit(GameManager.backdrop, (0, 0))
        
    @staticmethod
    def draw_dynamic_background():
        """
        Draws static grass on the screen, but shows different sections of the mountains based on the angle we have accumulated from the track.
        
        ### How the scrolling works:
        
        - Always render the full height of the mountains
        - When angle is 0, use x=0 -> x=WIDTH as the x range to show.
        - since `mtns_img` is 4320x300px, 1 degree is 4320/360 = 12px
        
        Thus, the x-coord of the left side should be `angle * 12`, and the right side should be `angle * 12 + WIDTH`
        """
        
        angle = GameManager.accumulated_angle % 360
        crop_pos_on_img = round(angle*12), 0
        size_of_crop = WIDTH, HEIGHT - GameManager.grass.get_height()
        
        GameManager.screen.blit(GameManager.backdrop, (0, 0), (*crop_pos_on_img, *size_of_crop))
        
        if angle > 360-math.degrees(FOV):
            # we ran past the right side of the png.
            # so, in addition to the x=0 blit, we need to do an x= 12*(360-angle) blit
            # we can actually omit the size, since it can just overflow off the screen
            GameManager.screen.blit(GameManager.backdrop, (round(12*(360-angle)), 0))        
            
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
        - quit_button
        """
        GameManager.create_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.create_game_button.update(GameManager.screen)
        
        GameManager.join_game_input.draw(GameManager.screen)
        
        GameManager.join_game_button.changeColor(pygame.mouse.get_pos())
        GameManager.join_game_button.update(GameManager.screen)
        
        GameManager.quit_button.changeColor(pygame.mouse.get_pos())
        GameManager.quit_button.update(GameManager.screen)

    @staticmethod 
    def draw_car(pos_y: float):
        """
        If currently in a crash, draws an explosion.
        
        Draws the car in the bottom-ish of the screen (80% of y)
        
        Moves it left and right depending on our y position.
        
        If our `pos[1] < 0`, render closer to the left side
        If our `pos[1] > 0`, render closer to the right side
        
        The offset is linear, with our car being positioned at x=20 when pos[1] is the map's width/2 - oob_leniency,
        and x=WIDTH-20 when pos[1] is the map's width/2 + oob_leniency.
        """
        
        vertical_pos = 4*HEIGHT/5 - GameManager.car.get_height()/2
        
        # calculate the offset
        total_x_range = WIDTH - 40 - GameManager.car.get_width() # 20px padding on each side, plus the width of the car
        total_track_width = GameManager.map_data['width'] + 2*GameManager.map_data['oob_leniency']
        proportion_of_total_range = (pos_y + total_track_width/2) / total_track_width
        
        horizontal_pos = 20 + proportion_of_total_range * total_x_range
        
        # draw explosion if there is a crash_end timestamp in the future
        time_until_crash_end = GameManager.crash_end_timestamp - time_ns()/1e9
        if time_until_crash_end > 0:
            
            # recalculate horizontal pos based on last_y_pos
            proportion_of_total_range = (GameManager.last_y_pos + total_track_width/2) / total_track_width
            horizontal_pos = 20 + proportion_of_total_range * total_x_range
            
            # Crashes should last 5 seconds. We pick which frame to use (0->77) based on how many seconds left
            frame_index = int(78*(5 - time_until_crash_end)/5)
            boom_frame = GameManager.boom.images[frame_index].convert_alpha()
            
            # scale image by 2x
            boom_frame = pygame.transform.scale(boom_frame, (boom_frame.get_width()*2, boom_frame.get_height()*2))
            
            # draw explosion at bottom-center of screen
            
            # we use horizontal pos from the car, but we center the explosion vertically
            vertical_pos = 450
            
            GameManager.screen.blit(boom_frame, (horizontal_pos, vertical_pos))
            GameManager.boom.next()
            return
        
        GameManager.screen.blit(GameManager.car, (horizontal_pos, vertical_pos))
    
    @staticmethod 
    def quit_game():
        """
        Exits the game gracefully.
        """
        print(f"\x1b[35mQuitting the game gracefully...\x1b[0m")
        
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
    """

    orig_width = 500
    orig_height = 450

    width = 1200 
    height = 240 
    
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
            vel: number,
            acc: number,
            angle: number, // in degrees
            hitbox_radius: number,
            keys: [forward: bool, backward: bool, left: bool, right: bool],
          is_crashed: bool
          }
        }
        ```
        """
        
        print(f"\x1b[35mCreating RenderingManager with {len(init_entities)} entities\x1b[0m")
        
        self.world = World(GameManager.map_data)
        self.road_animator = RoadAnimator(self.world.gamemap)
        self.last_render_time = time_ns()
        
        for entity in init_entities:
            self.place_entity(entity)

    def render_frame(self):
        """
        Draws on the screen a single frame based on the current state of the internal physics engine.
        """
        us = GameManager.get_our_entity()
        
        GameManager.draw_dynamic_background()
        
        road_image = self.road_animator.get_next(us.pos[0])
        
        deltatime = (time_ns() - self.last_render_time) / 1e9
        self.last_render_time = time_ns()
        
        # vanishing_point_loc = self.world.gamemap.vanishing_point_at(us.pos[0])
        
        # add to accumulated angle. Also mult by velocity/100 (at 0 speed we shouldnt be turning)
        GameManager.accumulated_angle += self.world.gamemap.angle_at(us.pos[0]) * ANGLE_ACCUMULATION_FACTOR * deltatime * us.vel/100
        
        GameManager.draw_road(road_image) 
        
        # draw entities
        self.draw_all_other_entities(us)
        
        GameManager.draw_car(us.pos[1])
        
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
        
        `data` should have the same schema as the `World.get_world_data` function, which looks like this:
        ```typescript
        [
          {
            username: string,
            color: string,
            physics: {
              pos: [pos_x: number, pos_y: number],
              vel: number,
              acc: number,
              angle: number, // in degrees
              hitbox_radius: number,
              keys: [forward: bool, backward: bool, left: bool, right: bool],
          is_crashed: bool
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
        
    def draw_all_other_entities(self, us: 'Entity'):
        sorted_by_dist = sorted(GameManager.get_all_other_entities(), key=lambda e: (e.pos[0] - us.pos[0])**2)
        for other in sorted_by_dist:
            
            # if other is behind us, don't draw it
            if other.pos[0] < us.pos[0] - 20: # some arbitrary fov expansion
                continue
            
            size = RenderingManager.get_rendered_size(us, other)
            if size < 10:
                continue
            
            offset = self.get_entity_center_offset(us, other)
            
            horizontal_pos = WIDTH / 2 + offset
            vertical_pos = RenderingManager.get_y_pos(other)
            
            if vertical_pos is None:
                continue # if the entity is behind us, don't draw it
        
            RenderingManager.draw_entity(size, (horizontal_pos, vertical_pos), other.color, other.is_crashed)
            
    @staticmethod
    def get_rendered_size(us: 'Entity', other: 'Entity') -> int:
        """
        Returns a size in px for the entity based on how far away and at what angle it is from us.
        
        Calculation formula:
        `size = 300 e^(-0.0015*dist)
        
        ### Note: With this formula (and the `if size < 30` check in `render_frame`), 
        # entities will not be rendered if they are more than 300m away (0 size).
        """
        
        dist = other.pos[0] - us.pos[0]
        
        # theta = (math.asin(other.hitbox_radius / (dist + other.hitbox_radius))) # For old system
         
        width_on_screen = min(400, 300 * math.exp(-0.015*dist)) if dist < 300 else 0
        return round(width_on_screen)
        
    @staticmethod
    def get_y_pos(other: 'Entity') -> int | None:
        """
        Returns a y-position on the screen based on an entity's distance from us.
        If the entity is behind us, returns None (don't draw it)
        
        The idea is that farther away entities should be drawn higher up (lower y-value)
        because they are closer to the horizon.
        
        Will not return a value lower than 300 (the horizon)
        and higher than 600 (bottom of screen, with some padding ofc)
        
        ### The function used for this calculation
        (can be changed - i just picked a random asymptotic decay from 600->300 in desmos)
        
        y_coord = `50000/(9*dist+100) + 220`
        """    
        
        us = GameManager.get_our_entity()
        
        dist = other.pos[0] - us.pos[0]
        if dist < 0: return None # if behind us, don't draw (draw at bottom of screen)
        return round(50000/(9*dist+100) + 220)

    def get_entity_center_offset(self, us: 'Entity', other: 'Entity') -> int:
        """
        @see - https://www.desmos.com/calculator/gtp9vomuej (equations for rendering math)
        
        Returns how far from the center of the screen (in pixels)
        an enemy entity should be placed, taking into account the apparent curvature of the road and the entity's y-pos (horizontal)
        
        For example, if the road ahead is straight, entities are rendered directly in front of us.
        If the road is curving to the right, entities are rendered more to the right side.
        """
        
        #################### OFFSET BASED ON ENEMY Y-POS ####################
        track_width = self.world.gamemap.map_data['width']
        
        # how far right/left to place them based on their y-pos (horizontal pos)
        y_pos_offset = other.pos[1] * (2*WIDTH/3)/(track_width) 
        
        # because of one vanishing-point perspective, this offset diminishes as we get farther away
        # The equation below provides approx. scale 1 when close, approx. scale 0.5 at 166.7m, scale 0 at 333.3m.
        # However, we should not render entities that are >300m away.
        enemy_x_dist = other.pos[0] - us.pos[0]
        
        y_pos_offset_distance_scale = max(0.01, 0.3+0.7*math.exp(-0.00005 * enemy_x_dist**2)) if enemy_x_dist > 0 else 1 # if behind us, don't squeeze back into middle
        
        ######################################################################
        
        ################### OFFSET BASED ON ROAD CURVATURE ###################
        curvature_offset = self.world.gamemap.angle_at(us.pos[0]) * (0.03 * enemy_x_dist)**1.2 
        ######################################################################
        
        # print(f"color={other.color} curv={curvature_offset} + y_pos={y_pos_offset}*y_pos scale={y_pos_offset_distance_scale}")
        
        return curvature_offset + y_pos_offset * y_pos_offset_distance_scale

    @staticmethod
    def angle_offset(other: 'Entity'):
        #-> Union[int, None]
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
    def draw_entity(size: int, pos: tuple[int, int], color: str, is_crashed: bool = False):
        """
        Draws an entity on the screen, given a size, offset, and color.
        
        Renders a crash animation if the `crash_progress` param is given.
        """
        
        if is_crashed:
            # just draw 20th frame
            boom_frame = GameManager.boom.images[19].convert_alpha()
            
            # scale image by 2x, and also by the given size
            boom_frame = pygame.transform.scale(boom_frame, (2*size, 2*size))
            
            # draw explosion at the calculated pos
            GameManager.screen.blit(boom_frame, pos)
            GameManager.boom.next()
            return
        
        car_image = CARS[color]
        
        height_to_width_ratio = car_image.get_height() / car_image.get_width()
        scaled_entity = pygame.transform.scale(car_image, (size, round(size * height_to_width_ratio)))
        
        pos = (pos[0] - scaled_entity.get_width()/2, pos[1] - scaled_entity.get_height()/2) # center
        
        GameManager.screen.blit(scaled_entity, pos)        
        
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
        self.registered_events = {}
        #: Dict[str, Callable[[Dict], Any]]
        """ Should be a dict mapping event names to callback functions. """
        
        return
    
    def connect(self, username: str):
        #-> Union[str, None]
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
                    
                    try:
                        payload = json.loads(raw_data[1:].decode('utf-8'))
                    except json.decoder.JSONDecodeError as e:
                        print(f"\x1b[31mError decoding JSON (skipping): {e}\x1b[0m")
                        continue
                    
                    # prefixing: first byte will be a '0' for events, '1' for packet data
                    if raw_data[0] == 1: 
                        self.on_packet(payload)
                        continue

                    event_name = payload.get('type')
                    data = payload.get('data')
                    
                    # data could be a list or dict, depending on the event (since its JSON)
                    
                    _callable = self.registered_events.get(event_name)
                    if not (_callable is None): 
                        print(f"\x1b[35mHandling Event \x1b[33m{event_name}\x1b[0m")
                        _callable(data)
                    else:
                        print(f"\x1b[2mIgnoring Unhandled event \x1b[0m\x1b[33m{event_name}\x1b[0m")
            except (ConnectionAbortedError, ConnectionResetError) as e:
                print(f"\x1b[31mConnection to server disrupted!\x1b[0m")
                
                # show a popup using tkinter
                GameManager.tk_root.withdraw()
                messagebox.showerror("Connection Error", "The connection to the server was disrupted. You might want to restart the game.")
                
                        
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
            username: string,f
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
        
        GameManager.game_renderer.set_physics(world_data)
                
    def on(self, event_name, callback) -> None:
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
        
        # if timestamp < GameManager.crash_end_timestamp, ignore all keys
        if time_ns()/1e9 < GameManager.crash_end_timestamp:
            return
        
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
            return {"success": False, "message": f"An error occured! Please try again. ({e})"}

def init_managers():
    """
    Run on game start
    """
    GameManager.socket_man = SocketManager()