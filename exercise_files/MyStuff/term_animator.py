""" Animates multiple trails on the screen. Trail attributes can be externalised as a json file. """
from collections import deque
from enum import Enum
import json
from math import sin, cos, atan2, radians, degrees
import os
from pathlib import Path
import sys
import time
import traceback
from termcolor import colored, COLORS

FRAMERATE = 20
SCRIPT_DIR = Path(__file__).parent

class InvalidTrail(Exception):
    def __init__(self, trail_name, *args: object) -> None:
        super().__init__(f"{trail_name}:", *args)

class Canvas:
    """ A canvas has a width and height, and a grid that is initialised as empty locations,
    and is used to track where where we are, and where we've been. """
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._grid = [[' ' for x in range(self._x)] for y in range(self._y)]
        self._trails = []

    def add_trail(self, trail):
        """ Used to add a Trail to the list of trails associated with this canvas. 
        Typically called by the Trail to register itself. """
        self._trails.append(trail)

    def x_out_of_bounds(self, point):
        if round(point[0]) < 0 or round(point[0]) >= self._x:
            return True

        return False
    
    def y_out_of_bounds(self, point):
        if round(point[1]) < 0 or round(point[1]) >= self._y:
            return True

        return False
        
    def hits_wall(self, point) -> tuple[int, int]:
        """" If we reach a wall, we return -1 for that axis. Otherwise, return 1 for that axis. """
        x_flip = -1 if self.x_out_of_bounds(point) else 1
        y_flip = -1 if self.y_out_of_bounds(point) else 1

        return x_flip, y_flip

    def set_pos(self, pos, mark):
        """ Set the (x, y) position to the provided character on the canvas. """
        # grid locations can only be ints, but the pos can itself be a float
        self._grid[round(pos[0])][round(pos[1])] = mark

    def _clear(self):
        """ Clear the terminal (used to create animation) """
        os.system('cls' if os.name == 'nt' else 'clear')

    def animate(self, framerate: int):
        """ Draws all trails in parallel. """
        while True:
            responses = [trail.execute_next_instruction() for trail in self._trails]
            self._render()
            time.sleep(1/framerate)
            if not any(responses):
                break # quit when no animators have any steps left

    def _render(self):
        """ Clear the terminal and then print each line in the canvas """
        self._clear()
        for y in range(self._y):
            print(' '.join([row[y] for row in self._grid]))

    def __str__(self) -> str:
        return "\n".join(str("".join(row)) for row in self._grid)
    
    def __repr__(self) -> str:
        return f"Canvas(x={self._x},y={self._y})"

class Vector(Enum):
    """ Vector Enum, where values are angles relative to y vertical, and increase clockwise.
    I.e. E is 0 and S is 90. """
    N = 0
    E = 90
    S = 180
    W = 270

class TerminalTrail:
    """ A moving head that leaves a trail. It follows instructions, #
    which can be an angle, or a move forward in the current direction.
    The TerminalTrail must register itself with a canvas, which is able to draw the trail. """

    TRAIL = '.'
    HEAD = '*'

    def __init__(self, canvas: Canvas, name, start=(0,0), instructions=None, trail_colour="green"):
        """ Set canvas, framerate, initial position, and instructions.
        Where an instruction repeats for n steps, expand this instruction
        into multiple instructions. """
        self._canvas = canvas
        self._name = name
        self._trail_colour = trail_colour
        if trail_colour not in COLORS:
            raise InvalidTrail(name, f"Invalid colour: {trail_colour}")
        
        self._pos = start
        if self._canvas.x_out_of_bounds(start) or self._canvas.y_out_of_bounds(start):
            raise InvalidTrail(name, f"Invalid start {start} for canvas {repr(canvas)}")
        
        self._vector_angle = Vector.E.value  # arbitrary initial vector as degrees

        self._instructions = deque()
        if instructions: # expand instructions so we can run individual steps in parallel
            for cmd, value in instructions:
                try:
                    value = int(value)
                except ValueError as e:
                    raise InvalidTrail(name, f"Bad instruction {cmd, value}") from e
                
                if cmd == "forward":
                    for _ in range(value):  # turn any ("forward", n) into n * (forward, 1)
                        self._instructions.append([cmd, 1])
                elif cmd == "angle":
                    self._instructions.append([cmd, value])
                else: # assume that the instruction maps to a function name
                    try:
                        getattr(self, cmd)
                    except AttributeError as e:
                        raise InvalidTrail(name, f"Bad instruction {cmd, value}") from e  
                                           
                    self._instructions.append([cmd, value])
        
        self._canvas.add_trail(self) # register this trail with the canvas

    def execute_next_instruction(self):
        """ Pop and process the next instruction.
        If it's a direction change, perform it, and then do the next move instruction. """
        if not self._instructions:
            return False # signal we've finished

        cmd, value = self._instructions.popleft()
        while cmd == "angle": # process any angle instructions, until we get to move
            self.set_direction_angle(value)
            cmd, value = self._instructions.popleft()

        if cmd == "forward":
            for _ in range(value):
                self.forward()
        else:
            getattr(self, cmd)(value)

        return True

    def set_direction_angle(self, angle: int):
        """ 0 degrees is pointing right. Angle is clockwise. """
        self._vector_angle = angle

    def forward(self, steps=1):
        """ Move n steps in the current direction """

        # set vector using unit circle, i.e. hyp = 1
        vector = TerminalTrail.get_vector_from_angle(self._vector_angle)
        for _ in range(steps):
            newpos = [self._pos[0]+vector[0], self._pos[1]+vector[1]]
            x_flip, y_flip = self._canvas.hits_wall(newpos) # if we bounce off a wall
            vector = x_flip*vector[0], y_flip*vector[1]
            new_angle = TerminalTrail.get_angle_for_vector(vector) # because y vector increments down
            if new_angle < 0:
                new_angle = 360 + new_angle

            self._vector_angle = new_angle
            newpos = [self._pos[0]+vector[0], self._pos[1]+vector[1]]

            self._update_posn(newpos)

    @staticmethod
    def get_vector_from_angle(angle_in_degrees):
        """ Return the unit (x,y) vector for a given angle """
        vector = (round(sin(radians(angle_in_degrees)), 2),
                  round(-cos(radians(angle_in_degrees)), 2))
                  
        return vector
    
    @staticmethod
    def get_angle_for_vector(vector: tuple):
        return degrees(atan2(vector[0], -vector[1]))

    def _move(self, direction: int):
        """ Update current direction, then draw """
        self.set_direction_angle(direction)
        self.forward()

    def _update_posn(self, pos):
        """ Updates the canvas, then renders the canvas """
        self._canvas.set_pos(self._pos, colored(TerminalTrail.TRAIL, self._trail_colour)) # old posn
        self._pos = pos # Update position
        self._canvas.set_pos(self._pos, colored(TerminalTrail.HEAD, 'red'))

    def draw_square(self, edge_len: int):
        """ Expand the square instruction into a list of instructions """
        self._instructions = deque()
        for direction in (Vector.E, Vector.S, Vector.W, Vector.N):
            self._instructions.append(["angle", direction.value])
            for _ in range(edge_len):
                self._instructions.append(["forward", 1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._instructions}"

def main(out = sys.stderr):
    my_canvas = Canvas(25, 25)

    with open(Path(SCRIPT_DIR, "animations.json"), "r", encoding="utf8") as f:
        data = json.load(f) # animators in stored in external json

    for shape_name, attribs in data.items():
        try:
            TerminalTrail(my_canvas, name=shape_name,
                      start=attribs["start"], instructions=attribs["steps"], trail_colour=attribs["colour"])
        except InvalidTrail as err:
            print(f"\n***\nInvalidTrail exception caught:\n{repr(err)}\n***", file=out)
            traceback.print_exc(file=out)
            
    my_canvas.animate(FRAMERATE)

if __name__ == '__main__':
    with open(Path(SCRIPT_DIR, 'term_animator.err'), 'w') as err_f:
        main(err_f)
