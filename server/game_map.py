from typing import List
from CONSTANTS import MAPS
import random

class CurveSegment:
    """
    A struct that represents a curved segment of the track
    
    ### How curves work:
    - The track should be rendered straight on the screen until the player's `x` position reaches `start_x`.
    - When they cross `start_x`, the track should begin curving with a linear increase in angle
    until the player's `x` position reaches `mid_x`, where the vanishing point should be at `theta_f`, relative to the FOV.
    - Angle of vanishing point should be linearly interpolated between `start_x` and `mid_x`, and same for `mid_x` and `end_x`.
    - When the player's `x` position reaches `end_x`, the track should be rendered straight again.
    
    Positive angles make the track curve to the right, and negative angles make the track curve to the left.
    """
    
    def __init__(self, start_x: int, mid_x: int, end_x: int, theta_f: int):
        self.start_x = start_x
        self.mid_x = mid_x
        self.end_x = end_x
        self.theta_f = theta_f
        
    def angle_at(self, pos_x: int) -> int:
        """
        Returns the angle of the track at a certain x position.
        """
        
        if pos_x < self.start_x or pos_x > self.end_x:
            return 0 # return angle of 0 (straight track)
        
        # NOTE postcondition: pos_x in [start_x, end_x]
        # interpolate angles
        if pos_x < self.mid_x:
            # interpolate between start_x and mid_x
            return self.theta_f * (pos_x - self.start_x) / (self.mid_x - self.start_x) 
        else:
            # interpolate between mid_x and end_x
            return self.theta_f * (self.end_x - pos_x) / (self.end_x - self.mid_x)

class GameMap:
    """
    Represents a racetrack object and its information, such as length and world record time.
    """
    
    def __init__(self, map_name: str = None):
        """
        Creates a new GameMap object. If no map name is provided, a random map is picked.
        """
        
        if map_name is None: map_name = random.choice(list(MAPS.keys()))
        
        elif not map_name in MAPS.keys():
            raise ValueError(f"Map name {map_name} not found in maps list!")
        
        self.map_name = map_name
        self.map_data = MAPS[map_name]
        """
        Format:
        ```typescript
        {
          map_name: string,
          map_file: string, // the file inside ./maps, on both the server and client
          preview_file: string, // the file the client should load as a waiting room preview img
          backdrop_file: string, // the file the client should load as the backdrop
          length: number,
          width: number,
          oob_leniency: number, // how far off the track the player can go before they are crashed
        } 
        ```
        """
        
        self.segments = self.parse_map_file()
        
    def parse_map_file(self) -> List[CurveSegment]:
        """
        Parses a .map file and returns a list of CurveSegments.
        
        A .map file is a text file where each line represents a CurveSegment.
        These segments should be SORTED. Since no segments can overlap, this means that
        the start_x of each segment should be greater than the end_x of the previous segment.
        
        The file should be formatted as follows:
        
        ```
        1 | start_x,mid_x,end_x,theta_f
        2 | start_x,mid_x,end_x,theta_f
        3 | ...
        ```
        
        Here is an example:
        ```
        400,600,800,30
        1200,1600,2000,20
        2400,2600,2800,-30
        ```
        """
        
        segments = []
        
        with open(f"./server/maps/{self.map_data['map_file']}", "r") as f:
            for line in f.readlines():
                start_x, mid_x, end_x, theta_f = line.split(",")
                segments.append(CurveSegment(int(start_x), int(mid_x), int(end_x), int(theta_f)))
                
        return segments      
    
    def curvesegment_at(self, pos_x: float) -> CurveSegment | None:
        """
        Returns the CurveSegment defined at a certain x position.
        
        If there is no segment at that position, returns None.
        """
        
        # since there are a small number of segments, a linear search should be fine
        for segment in self.segments:
            if pos_x >= segment.start_x and pos_x <= segment.end_x:
                return segment
        
        return None
    
    def angle_at(self, x_pos: float) -> int:
        """
        Returns the angle at the current x-position based on the map. 
        
        For example, if the road is currently straight at `x_pos`, this will return `0`.
        If we are beginning to enter a left curve, this will return something like `-10`.
        If we are at the climax of a left curve, this will return a more extreme negative number (say, `-45`) based on the curve's angle (defined by the map).
        
        ### Here's how this calculation is made:
        - The map is made of `CurveSegments`, each of which have a `theta_f` field that determines their maximum curvature.
        - `CurveSegments have a ramp-up and ramp-down period, where the curvature changes linearly.
        - `We will take the `q1` and `q3` points of the curve, which are the averages of start-mid and mid-end of a curve respectively. A diagram is below:
        
        `S-------Q1-------M---Q3---E`
        
        - For the period between `S` and `Q1`, the angle is calculated linearly from `0` to `theta_f`.
        - For the period between `Q1` and `Q3`, the angle is constant at `theta_f`.
        - For the period between `Q3` and `E`, the angle is calculated linearly from `theta_f` to `0`.
        """
        
        curr_curvesegment = self.curvesegment_at(x_pos)
        
        if curr_curvesegment is None:
            # No curvature
            return 0
    
        curvesegment_rampup_length = curr_curvesegment.mid_x - curr_curvesegment.start_x
        curvesegment_rampdown_length = curr_curvesegment.end_x - curr_curvesegment.mid_x
        
        start = curr_curvesegment.start_x
        q1 = curr_curvesegment.mid_x - curvesegment_rampup_length/2
        q3 = curr_curvesegment.mid_x + curvesegment_rampdown_length/2
        end = curr_curvesegment.end_x

        if x_pos > start and x_pos < q1:
            self.curve_percentage = (x_pos - start) / (q1 - start)
            return curr_curvesegment.theta_f * self.curve_percentage
        elif x_pos > q1 and x_pos < q3:
            # just return the full angle
            return curr_curvesegment.theta_f
        elif x_pos > q3 and x_pos < end:
            self.curve_percentage = (x_pos - q3) / (end - q3)
            return curr_curvesegment.theta_f * (1 - self.curve_percentage)