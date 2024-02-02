# Overview
Developers:

- User Experience, Texturing, Sprites - Sindhura and Camila 
- Testing and Debugging – Angus
- Physics, Balancing - Aidan
- Architecture, Rendering, UI Design – Michael

# Architecture
The main idea for our version of Pole Position is the addition of **live multiplayer**. For our complete game system, this means we have two branches - a client side, responsible for rendering interfaces and handling all user inputs, and a server side, which deals with the game logic and communication between clients.

The nature of storing so many different connections and handling a variety of events means our branches heavily leverage OOP.

We also implement a **room system**, where players can create rooms for others to join using a 6-digit alphanumeric code. Once a room is created or joined into, a racetrack ("map") is selected randomly from our library. Players are then entered into a waiting lobby where the host has the sole authority to start the game.

Once a game has started, all relevant client keyboard inputs are broadcast to the server, which handles all physics and verifies game logic. The server calculates new physics and distributes all this data to every connected client, who can then update their displays accordingly.

## Server
The server is written with Python's `flask` and `socket` libraries. The server is actually split into many different modules itself, most notably differentiating between **HTTP** endpoints and **socket** endpoints.

The most important part of the server is that it runs a multitude of threads. Since we are running an online game, code that stops the main process (known as **blocking calls**) disrupt the server's ability to broadcast live data and calculate physics in real time. However, certain blocking calls, like waiting for a client's keyboard input, are required for a responsive game.

The solution is to run each of these task groups on its own separate thread. This way, the host machine can handle of the following simultaneously:

- HTTP requests
- Socket connections
- Socket reception and broadcasting
- Physics calculations
- Checking for game end conditions
- Dealing with room creation and disbandment

### Game flow
The server bases game flow off `Room` and `Client` objects.

Client objects are created when a client completes a socket handshake with the server. Each client has a unique `client_id` field, which is bound to the client's socket connection. The server uses this `client_id` to identify users and different sockets within the same room.

Rooms are created when a client requests to create a room. Each room has a unique `room_id` field, which is used to identify the room and is also used as the room code. Rooms are destroyed in the following cases:
- The host leaves the room in the waiting lobby
- The game ends and all members have left

When a host client clicks the "Start Game" button, an HTTP request is made to the `/startgame` endpoint which marks the `Room` object that the client is hosting to `started=True`. Once this happens, a timestamp is broadcast to all clients marked by the `game-init` event (see events section). Clients are then instructed to proceed to a countdown screen. Once this start timestamp is reached, the client program will begin rendering world data and listening for keypresses to send to the server.

### Physics
Most importantly, all physics are handled on the server side. While the client does have matching a matching physics engine, all data on the client side is overwritten by server-side physics upon receiving a packet, which are broadcasted from the server **every 0.25 seconds**. This is to prevent cheating and to ensure that all clients are in sync. The server also handles all collisions and out-of-bounds penalties. When a client crashes, the server sends a `crash` event to the client, which triggers a crash animation and sets new physics.

Overall, velocity and acceleration are limited to realistic values for a racecar (about 200 miles per hour maximum). 

## Client
The client side is written primarily using the `pygame` library. This is where all the game's rendering and user input handling is done. The principal structure of the client side is also broken up into separate modules. Specifically, four main "managers" exist as a framework for our game:

- `GameManager` - which stores/manipulates general variables and resources, such as the `screen` object
- `RenderingManager` - which handles placing sprites and animations on screen depending on the current world information (such as the player's current position, and the positions of other players)
- `SocketManager` - which handles all live communication (keyboard inputs and events) between the server and client.
- `HTTPManager` - which handles all one-time requests and setup for the game, like joining/creating rooms, starting the game, etc.

### Rendering
Since racing games are generally three-dimensional, we initially experimented with a custom-built rendering engine. However, since Pole Position was never an open-world game, much of the functionality of a 3D renderer was actually counterproductive - for example, since players are not permitted to stray too far from track boundaries, there is no reason to handle entity rendering from different angles.

Our track rendering uses handmade textures which are specifically selected and animated based on current world information, most notably, where on the map a player is. If the map data and player position currently specify that the track is curved, a curved animation of the track is rendered on screen. 

Entities (other players) are also 2D textures which are scaled based on their distance from the player. If another object is ahead of the camera (which is defined as the client's entity), its size on screen is calculated using a simple projection formula.

Lastly, the background of maps scroll based on the angle accumulated through any track turning. If a player's position currently coincides with a curved track, then an `accumulated_angle` global field is slowly incremented or decremented based on the track direction, curvature, player angle, and player velocity. This accumulated angle parameter is directly responsible for the section of the background panorama ("skybox") that is rendered visible on screen.

### Event System
`SocketManager` implements an asynchronous, multithreaded event system that allows the server to spontaneously send data to the client. The structure for this system was inspired by Javascript's event-based `socket.io` library.

`SocketManager` objects provide an `on` method, which allows the client to register a callback function for a specific event. When the server sends an event with the same name, the client's callback function is called with the data from the server.

The event listener loop is started when the socket completes an initial handshake with the server and remains active while the client program is open. The following events are currently implemented:

- `leave` - as a confirmation or alert that the receiving client has been removed from their current room
- `game-end` - as a signal that the game has ended. Also carries a payload of leaderboard data which is shown on the Game Over screen.
- `game-init` - as a signal that the host has started the game. Because a delay is implemented between the host's start request and the actual game start, this event delivers to all clients a consensus timestamp for when to begin rendering the live world.
- `crash` - used for when the server detects that the player has collided with either the track boundaries or another entity. This event is used to trigger a crash animation and respawn physics.
- `player-join` - raised when a new player joins the room. This event is used to update the lobby screen with the new player's username and racecar color.
- `player-leave` - raised when a player leaves the room. This event is used to remove the player from the lobby screen.

### Keyboard Input Protocol
There are eight different controls we need to handle in our game - the four arrow/WASD keys being pressed or released. To reduce network traffic, each keyboard input is sent as a single byte of data. Keyboard input is encoded as follows:

- `000` - forward keyup
- `001` - backward keyup
- `010` - left keyup
- `011` - right keyup
- `100` - forward keydown
- `101` - backward keydown
- `110` - left keydown
- `111` - right keydown

When `pygame.event.get()` on the client-side contains relevant key presses, the type and action of the event are encoded and sent as a packet to the server, which then decodes the packet and updates the player's physics accordingly. 

# Major server-side external libraries
- `Flask` [https://flask.palletsprojects.com/en/3.0.x/]((Docs))
- `socket` [https://docs.python.org/3/library/socket.html]((Docs))
- `threading` [https://docs.python.org/3/library/threading.html]((Docs))

# Major client-side external libraries
- `pygame` [https://www.pygame.org/docs/]((Docs))
- `httpx` [https://www.python-httpx.org/]((Docs))
- `socket` [https://docs.python.org/3/library/socket.html]((Docs))
- `threading` [https://docs.python.org/3/library/threading.html]((Docs))

# Design Choices:
It's mentioned later within the document, but as we started this project we didn't have much of a vision on how we were going to move the project forwards, which must have influenced our decision to create the live game in a way more familiar to us, so while the original game rendered in the game, the background road was hand-drawn frame by frame to create an animation to play in the background as the car went forwards. Because of this it creates a different look from the original game, with an interesting situatition where because of the straightness and better graphics seen today, but higher pixelation found from software made for lower quality art. It's part of what gives our game it's unique vibe, and is fun in it's own way after the almost tearjerking (not in the fun way) work it took to make the frames.

# Playing Instructions

The game requires a Python version of 3.10 or newer.

## TLDR
- Clone the repository `git clone https://github.com/crystaltine/PolePositionI.git PolePositionI`
- Open two or more terminals and set all working directories to the cloned repository `cd PolePositionI`
- Install required libraries (run once in one terminal) `pip install -r requirements.txt`
- In exactly one terminal, run the server: `python server/server.py`
- In all others, run the game: `python game/main.py`

While our game is mostly self explanatory once it's running, getting it to fun can be the fun - or difficult - part depending on your mood. You need to have a terminal open, and in there you run the server.py file found within the server folder to get the server running. You'll see a visual confirmation that it's working once you start running the file. Once you're done you can either open another terminal, or open your own Visual Studio Code/adjacent program and run the main.py file found within the game folder. This may take a couple seconds, but then the game screen will appear, and if you are going to be game host, click create game, or if you're joining a game click join game. Both options will prompt you for a username that you have to input, and then you'll appear in a lobby were the join code is visible and ready to be shared. Then once everybody is in the lobby, the lobby host can hit start game and all players have to get ready, get set, and GO!

# User Experience 
The experience for a first-time user is intuitive. When the game is first launched, there are buttons on the main menu screen to create a game, join a game with a room code, and to quit. Once a game is made, the host is sent to a lobby screen in which they can wait for other players to join, or race by themselves. In the lobby screen, all players that have connected are displayed with a start game button on the bottom right that is available to the lobby host. The lobby host is signified with a crown over their car and is the person that started the game. Once the game has started, there is a countdown and the players are off, racing along the track until someone reaches the finish line. Once a player has reached the finish line, the game ends, and a snapshot of the leaderboard is displayed. A first-time user should launch the game and easily be able to race against friends or practice the mechanics of the game.

Players will know what to do because the design is intuitive and is very similar to many popular multiplayer games such as Among Us. Even players who are not avid gamers will know to hit a create game and start game button. Racing games as a genre are also very user-friendly with intuitive mechanics. 

The gameplay feels predictable for an experienced player. Since we have only one map right now, players can get familiar with the positioning of the turns and straightaways. This, combined with our more realistic physics compared to the original game will reward players who are familiar with the course. Effective braking on turns will be necessary to get faster times. 

The main draw that will make players want to keep coming back is the fastest lap time feature. This is the game’s version of a high score and players will want to beat their previous record. There are also slightly punishing game mechanics such as crashing when going too far off the track. This can result from not braking before turns and will ruin lap times. This is an added layer of difficulty that should keep players coming back to the game. There’s also the competitive aspect that comes with racing against friends. Competition between players within the lobby should create tension and make the game more fun. 

## Retrospective:
The process of writing this app was challenging. Coordinating to complete a project even in a small team of 5 was difficult. For a lot of us, this was the largest project we have worked on and it was also complicated. There were many unexpected issues that arose and making this simple game turned out to be quite the challenge. 

Communication was also a challenge for a long time. In the beginning we didn’t have a clear vision of what we wanted to do and how we would even go about doing it. So this made communication very difficult. This lack of focus made many members feel lost and no one really had a clear idea of how we would make our game. However as our ideas formed and the project came to take shape, our communication ramped up along with it. The high point was this past week. We made a discord server at the beginning of the project and in the final week of development it was constantly buzzing with questions, answers, and ideas on what we could do. The deadline forced us to communicate more but a clearer vision also helped all of us in communication. 

There was constant iteration and large changes made during our process. Our physics were constantly changing and integrating into new systems was a regular occurence. The largest change was going from a map for our track,  to changing that to a constant straightline that would curve the track and change the perspective around the car while the car itself behind the scenes was always moving in a straightline. 

The main thing we would do differently next time is having mini deadlines throughout the development process. We needed some last-minute heroics from Michael to get all of our code fully integrated into our final working game and that was entirely avoidable. It’s nice to have a final product but the crunch time push from all of us was tiring and stressful. Multiple smaller deadlines would have pushed all of us to be more efficient with our time and avoid the last-minute finish we had. We could have also communicated better in the beginning of the project. The very beginning of the project was a very crucial time for us to get a clear vision of how we would make our game. Instead of spending a few periods talking as a team and having defined ideas, we didn’t communicate much and that set us back. 
