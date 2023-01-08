from enum import Enum
import os
import time
from termcolor import colored

# This is the Canvas class. It defines some height and width, and a 
# matrix of characters to keep track of where the TerminalScribes are moving
class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]

    def hits_wall(self, point):
        """" Returns True if the given point is outside the boundaries of the Canvas """
        return point[0] < 0 or point[0] >= self._x or point[1] < 0 or point[1] >= self._y

    def set_pos(self, pos, mark):
        """ Set the (x, y) position to the provided character on the canvas. """
        self._canvas[pos[0]][pos[1]] = mark

    def clear(self):
        """ Clear the terminal (used to create animation) """
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print(self):
        """ Clear the terminal and then print each line in the canvas """
        self.clear()
        for y in range(self._y):
            print(' '.join([col[y] for col in self._canvas]))

class Vector(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

class TerminalScribe:
    TRAIL = '.'
    MARK = '*'

    def __init__(self, canvas, framerate=10):
        self.canvas = canvas
        self.framerate = framerate
        self.pos = [0, 0]

    def move(self, direction: Vector):
        pos = [self.pos[0]+direction.value[0], self.pos[1]+direction.value[1]]
        if not self.canvas.hits_wall(pos):
            self.draw(pos)

    def draw(self, pos):
        # Set the old position to the "trail" symbol
        self.canvas.set_pos(self.pos, TerminalScribe.TRAIL)
        # Update position
        self.pos = pos
        # Set the new position to the "mark" symbol
        self.canvas.set_pos(self.pos, colored(TerminalScribe.MARK, 'red'))
        # Print everything to the screen
        self.canvas.print()
        # Sleep for a little bit to create the animation
        time.sleep(1/self.framerate)

    def draw_square(self, edge_len: int):
        for direction in (Vector.RIGHT, Vector.DOWN, Vector.LEFT, Vector.UP):
            for _ in range(edge_len):
                self.move(direction)

# Create a new Canvas instance that is 30 units wide by 30 units tall
my_canvas = Canvas(30, 30)

# Create a new scribe and give it the Canvas object
scribe = TerminalScribe(my_canvas)

scribe.draw_square(10)
