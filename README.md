## AN INTERESTING IDEA FOR WORLD REPERSENTATION:
We can basically store players as **point/shape objects**, each with pos, vel, acc. on a **2d plane**

This way, we can handle physics/collisions relatively easily - just check if a player's hitbox is
- colliding with another player
- colliding with a wall
- too far off the track
- out of bounds
- etc...

^ For this, we could do **circular hitboxes** to make collision detection much simpler and more efficient (just determine distance between points instead of having to factor in rotation and stuff)

We can also handle the camera relatively easily - on the client side, just do some scaling and other math to place enemy players correctly on the screen.

^^^ For example: if a player is rotated 0deg and an enemy is 400m away at 24deg, we could have a DISTANCE_SCALE function and a FOV function that calculates how small to make the player and how far off to the side to place the player on the screen.

Plus, doing this allows us to store tracks/maps pretty easily - just as a collection of points/shapes that define the track, and maybe a defining a certain radius around the track as the "track area" that players can't leave (or else they crash and respawn at the last checkpoint or something)

## TEMPORARY TODO/NOTES LIST
### im adding this because i need to not forget to do these things
#### plus its helpful if you guys know this too

- based on the new framework for handling networking, each server->client payload *with the exception of physics packets and the initial client_id message* must be a **serialized json object** in the following format:
 
- (see `server/server.py`): socket data will always start with a `1` byte or a `0` byte. `1` means that the data is a serialized json object **used exclusively for events**, and `0` means that the data is a packet that is used for physics.

```typescript
{
    type: str // basically an event name. When the client registers an event using socket_man.on(event_name, ...), this should be the event_name.
    data: any // the data to be sent to the client. This can be anything, but it must be serializable.
}
```

## ANOTHER IMPORTANT NOTE
Please use `GameManager.socket_man.socket.close()` on every `pygame.QUIT` event. This will close the socket connection gracefully and prevent a ghost client instance on the server.