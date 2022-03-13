import os
import time
from termcolor import colored, COLORS
import math 
import random

class TerminalScribeException(Exception):
    def __init__(self, message=''):
        super().__init__(colored(message, 'red'))

class InvalidParameter(TerminalScribeException):
    pass

class Canvas:
    def __init__(self, width, height):
        self._x = width
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]

    def hitsVerticalWall(self, point):
        return round(point[0]) < 0 or round(point[0]) >= self._x

    def hitsHorizontalWall(self, point):
        return round(point[1]) < 0 or round(point[1]) >= self._y

    def hitsWall(self, point):
        return self.hitsVerticalWall(point) or self.hitsHorizontalWall(point)

    def getReflection(self, point):
        return [-1 if self.hitsVerticalWall(point) else 1, -1 if self.hitsHorizontalWall(point) else 1]

    def setPos(self, pos, mark):
        try:
            self._canvas[round(pos[0])][round(pos[1])] = mark
        except Exception as e:
            raise TerminalScribeException('Could not set position to {} with mark '.format(pos, mark))

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print(self):
        self.clear()
        for y in range(self._y):
            print(' '.join([col[y] for col in self._canvas]))

class CanvasAxis(Canvas):
    # Pads 1-digit numbers with an extra space
    def formatAxisNumber(self, num):
        if num % 5 != 0:
            return '  '
        if num < 10:
            return ' '+str(num)
        return str(num)

    def print(self):
        self.clear()
        for y in range(self._y):
            print(self.formatAxisNumber(y) + ' '.join([col[y] for col in self._canvas]))

        print('  '.join([self.formatAxisNumber(x) for x in range(self._x)]))

def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

class TerminalScribe:
    def __init__(self, canvas, color='red', mark='*', trail='.', pos=(0, 0), framerate=.05, degrees=135):
        if not issubclass(type(canvas), Canvas):
            raise InvalidParameter('Must pass canvas object')
        self.canvas = canvas
        
        if len(str(trail)) != 1:
            raise InvalidParameter('Trail must be a single character')
        self.trail = str(trail)
        
        if len(str(mark)) != 1:
            raise InvalidParameter('Mark must be a single character')
        self.mark = str(mark)
        
        if not is_number(framerate):
            raise InvalidParameter('Framerate must be a number')
        self.framerate = framerate
        
        if len(pos) != 2 or not is_number(pos[0])or not is_number(pos[1]):
            raise InvalidParameter('Position must be two numeric values (x, y)')
        self.pos = pos

        if color not in COLORS:
            raise InvalidParameter(f'color {color} not a valid color ({", ".join(list(COLORS.keys()))})')
        self.color=color
        
        if not is_number(degrees):
            raise InvalidParameter('Degrees must be a valid number')
        self.setDegrees(degrees)

    def setPosition(self, pos):
        self.pos = pos

    def setDegrees(self, degrees):
        radians = (degrees/180) * math.pi 
        self.direction = [math.sin(radians), -math.cos(radians)]

    def bounce(self, pos):
        reflection = self.canvas.getReflection(pos)
        self.direction = [self.direction[0] * reflection[0], self.direction[1] * reflection[1]]

    def forward(self, distance):
        for i in range(distance):
            pos = [self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]]
            if self.canvas.hitsWall(pos):
                self.bounce(pos)
                pos = [self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]]
            self.draw(pos)

    def draw(self, pos):
        self.canvas.setPos(self.pos, self.trail)
        self.pos = pos
        self.canvas.setPos(self.pos, colored(self.mark, self.color))
        self.canvas.print()
        time.sleep(self.framerate)

class PlotScribe(TerminalScribe):
    def plotX(self, function):
        for x in range(self.canvas._x):
            pos = [x, function(x)]
            if pos[1] and not self.canvas.hitsWall(pos):
                self.draw(pos)

class RobotScribe(TerminalScribe):
    def up(self, distance=1):
        self.direction = [0, -1]
        self.forward(distance)

    def down(self, distance=1):
        self.direction = [0, 1]
        self.forward(distance)

    def right(self, distance=1):
        self.direction = [1, 0]
        self.forward(distance)

    def left(self, distance=1):
        self.direction = [-1, 0]
        self.forward(distance)

    def drawSquare(self, size):
        self.right(size)
        self.down(size)
        self.left(size)
        self.up(size)

class RandomWalkScribe(TerminalScribe):
    def __init__(self, canvas, degrees=135, **kwargs):
        super().__init__(canvas, **kwargs)
        self.degrees = degrees
    
    def randomizeDegreeOrientation(self):
        self.degrees = random.randint(self.degrees-10, self.degrees+10)
        self.setDegrees(self.degrees)
    
    def bounce(self, pos):
        reflection = self.canvas.getReflection(pos)
        if reflection[0] == -1:
            self.degrees = 360 - self.degrees
        if reflection[1] == -1:
            self.degrees = 180 - self.degrees
        self.direction = [self.direction[0] * reflection[0], self.direction[1] * reflection[1]]

    def forward(self, distance):
        for i in range(distance):
            self.randomizeDegreeOrientation()
            super().forward(1)

def sine(x):
    return 5*math.sin(x/4) + 15

def cosine(x):
    return 5*math.cos(x/4) + 15

def circleTop(x):
    radius = 10
    center = 20
    if x > center - radius and x < center + radius:
        return center-math.sqrt(radius**2 - (x-center)**2)

def circleBottom(x):
    radius = 10
    center = 20
    if x > center - radius and x < center + radius:
        return center+math.sqrt(radius**2 - (x-center)**2)


canvas = Canvas(40, 40)
scribe = TerminalScribe(canvas, color='lavender')
scribe.forward(10)
