from enum import Enum
from math import sin, cos, radians
import os
import time
from termcolor import colored

# This is the Canvas class. It defines some height and width, and a 
# matrix of characters to keep track of where the TerminalScribes are moving
class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._grid = [[' ' for x in range(self._x)] for y in range(self._y)]

    def hits_wall(self, point):
        """" Returns True if the given point is outside the boundaries of the Canvas """
        return (round(point[0]) < 0 or round(point[0]) >= self._x 
                or round(point[1]) < 0 or round(point[1]) >= self._y)

    def set_pos(self, pos, mark):
        """ Set the (x, y) position to the provided character on the canvas. """
        # grid markers can only be ints, but the pos can itself be a float
        self._grid[round(pos[0])][round(pos[1])] = mark

    def clear(self):
        """ Clear the terminal (used to create animation) """
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        """ Clear the terminal and then print each line in the canvas """
        self.clear()
        for y in range(self._y):
            print(' '.join([row[y] for row in self._grid]))

    def __str__(self) -> str:
        return "\n".join(str("".join(row)) for row in self._grid)

class Vector(Enum):
    N = 270
    E = 0
    S = 90
    W = 180

class TerminalAnimator:
    TRAIL = '.'
    HEAD = '*'

    def __init__(self, canvas, framerate=20):
        self._canvas = canvas
        self._framerate = framerate
        self._pos = [0, 0]
        self._vector_angle = Vector.E.value  # arbitrary initial vector as degrees

    def set_direction(self, angle: int):
        """ 0 degrees is pointing right. Angle is clockwise. """
        self._vector_angle = angle
    
    def forward(self, steps=1):
        """ Move n steps in the current direction """
        vector = (round(cos(radians(self._vector_angle)), 2), round(sin(radians(self._vector_angle)), 2))
        for _ in range(steps):
            pos = [self._pos[0]+vector[0], self._pos[1]+vector[1]]
            if not self._canvas.hits_wall(pos):
                self.draw(pos)
        
    def move(self, direction: int):
        """ Update current position, then draw """
        self.set_direction(direction)
        self.forward()

    def draw(self, pos):
        """ Updates the canvas, then renders the canvas """
        self._canvas.set_pos(self._pos, colored(TerminalAnimator.TRAIL, 'green')) # old posn
        self._pos = pos # Update position
        self._canvas.set_pos(self._pos, colored(TerminalAnimator.HEAD, 'red'))

        self._canvas.render()
        time.sleep(1/self._framerate)

    def draw_square(self, edge_len: int):
        for direction in (Vector.E, Vector.S, Vector.W, Vector.N):
            for _ in range(edge_len):
                self.move(direction.value)

# Create a new Canvas instance that is 30 units wide by 30 units tall
my_canvas = Canvas(30, 30)

# Create a new scribe and give it the Canvas object
scribe = TerminalAnimator(my_canvas)

scribe.draw_square(10)

scribe.set_direction(0)
scribe.forward(35)
scribe.set_direction(135)
scribe.forward(25)
scribe.set_direction(180)
scribe.forward(10)
scribe.set_direction(270)
scribe.forward(15)
scribe.set_direction(30)
scribe.forward(30)
