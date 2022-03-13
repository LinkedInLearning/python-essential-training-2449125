import os
import time
from termcolor import colored, COLORS
import math 
import random
from threading import Thread
from inspect import getmembers, ismethod

class TerminalScribeException(Exception):
    def __init__(self, message=''):
        super().__init__(colored(message, 'red'))

class InvalidParameter(TerminalScribeException):
    pass

def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

class Canvas:
    def __init__(self, width, height, scribes=[], framerate=.05):
        if not is_number(width):
            raise InvalidParameter('Width must be a number')
        self._x = width
        if not is_number(height):
            raise InvalidParameter('Height must be a number')
        self._y = height
        self._canvas = [[' ' for y in range(self._y)] for x in range(self._x)]
        self.scribes = scribes

        if not is_number(framerate):
            raise InvalidParameter('Framerate must be a number')
        self.framerate = framerate

    def toDict(self):
        return {
            'classname': type(self).__name__,
            'x': self._x,
            'y': self._y,
            'canvas': self._canvas,
            'scribes': [scribe.toDict() for scribe in self.scribes]
        }

    def fromDict(data):
        canvas = globals()[data.get('classname')](data.get('x'), data.get('y'), scribes=[globals()[scribe.get('classname')].fromDict(scribe) for scribe in data.get('scribes')])
        canvas._canvas = data.get('canvas')
        return canvas

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
            raise TerminalScribeException(e)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def go(self):
        max_moves = max([len(scribe.moves) for scribe in self.scribes])
        for i in range(max_moves):
            for scribe in self.scribes:
                threads = []
                if len(scribe.moves) > i:
                    args = scribe.moves[i][1]+[self]
                    threads.append(Thread(target=scribe.moves[i][0], args=args))
                [thread.start() for thread in threads]
                [thread.join() for thread in threads]
            self.print()
            time.sleep(self.framerate)

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

        print(' '.join([self.formatAxisNumber(x) for x in range(self._x)]))

class TerminalScribe:
    def __init__(self, color='red', mark='*', trail='.', pos=(0, 0), degrees=135):
        self.moves = []

        if color not in COLORS:
            raise InvalidParameter(f'color {self.color} not a valid color ({", ".join(list(COLORS.keys()))})')
        self.color=color

        if len(str(mark)) != 1:
            raise InvalidParameter('Mark must be a single character')
        self.mark = str(mark)

        if len(str(trail)) != 1:
            raise InvalidParameter('Trail must be a single character')
        self.trail = str(trail)
        
        if len(pos) != 2 or not is_number(pos[0])or not is_number(pos[1]):
            raise InvalidParameter('Position must be two numeric values (x, y)')
        self.pos = pos
        
        if not is_number(degrees):
            raise InvalidParameter('Degrees must be a valid number')
        self.setDegrees(degrees)

    def toDict(self):
        return {
            'classname': type(self).__name__,
            'color': self.color,
            'mark': self.mark,
            'trail': self.trail,
            'pos': self.pos,
            'moves': [[move[0].__name__, move[1]] for move in self.moves]
        }

    def fromDict(data):
        scribe = globals()[data.get('classname')](
            color=data.get('color'),
            mark=data.get('mark'),
            trail=data.get('trail'),
            pos=data.get('pos'),
            )
        scribe.moves = scribe._movesFromDict(data.get('moves'))
        return scribe

    def _movesFromDict(self, movesData):
        bound_methods = {key: val for key, val in getmembers(self, predicate=ismethod)}
        return [[bound_methods[name], args] for name, args in movesData]

    def _setPosition(self, pos, _):
        self.pos = pos

    def setPosition(self, pos):
        self.moves.append((self._setPosition, [pos]))

    def _setDirection(self, direction, _):
        self.direction = direction

    def setDirection(self, direction):
        self.moves.append((self._setDirection, [direction]))

    def degreesToUnitDirection(self, degrees):
        radians = (degrees/180) * math.pi 
        return [math.sin(radians), -math.cos(radians)]

    def _setDegrees(self, degrees, _):
        self.direction = self.degreesToUnitDirection(degrees)
    
    def setDegrees(self, degrees):
        self.moves.append((self._setDegrees, [degrees]))

    def bounce(self, pos, canvas):
        reflection = canvas.getReflection(pos)
        self.direction = [self.direction[0] * reflection[0], self.direction[1] * reflection[1]]

    def _forward(self, canvas):
        pos = [self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]]
        if canvas.hitsWall(pos):
            self.bounce(pos, canvas)
            pos = [self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]]
        self.draw(pos, canvas)

    def forward(self, distance=1):
        for i in range(distance):
            self.moves.append((self._forward, []))

    def draw(self, pos, canvas):
        canvas.setPos(self.pos, self.trail)
        self.pos = pos
        canvas.setPos(self.pos, colored(self.mark, self.color))

class PlotScribe(TerminalScribe):

    def __init__(self, domain, **kwargs):
        self.x = domain[0]
        self.domain = domain
        super().__init__(**kwargs)

    def toDict(self):
        data = super().toDict()
        data['x'] = self.x 
        data['domain'] = self.domain
        return data

    def fromDict(data):
        scribe = globals()[data.get('classname')](
            color=data.get('color'),
            mark=data.get('mark'),
            trail=data.get('trail'),
            pos=data.get('pos'),
            domain=data.get('domain'),
        )
        scribe.x = data.get('x')
        return scribe

    def _plotX(self, function, canvas):
        pos = [self.x, function(self.x)]
        if not canvas.hitsWall(pos):
            self.draw(pos, canvas)
        self.x = self.x + 1

    def plotX(self, function):
        self.x = self.domain[0]
        for x in range(self.domain[0], self.domain[1]):
            self.moves.append((self._plotX, [function]))

class RobotScribe(TerminalScribe):
    def up(self, distance=1):
        self.setDirection([0, -1])
        self.forward(distance)

    def down(self, distance=1):
        self.setDirection([0, 1])
        self.forward(distance)

    def right(self, distance=1):
        self.setDirection([1, 0])
        self.forward(distance)

    def left(self, distance=1):
        self.setDirection([-1, 0])
        self.forward(distance)

    def drawSquare(self, size):
        self.right(size)
        self.down(size)
        self.left(size)
        self.up(size)

class RandomWalkScribe(TerminalScribe):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.degrees = kwargs.get('degrees', 135)
    
    def _randomizeDegrees(self, _):
        self.degrees = random.randint(self.degrees-10, self.degrees+10)
        self.direction = self.degreesToUnitDirection(self.degrees)
        print(f'Degrees is {self.degrees}')

    def randomizeDegrees(self):
        self.moves.append((self._randomizeDegrees, []))
    
    def bounce(self, pos, canvas):
        reflection = canvas.getReflection(pos)
        if reflection[0] == -1:
            self.degrees = 360 - self.degrees
        if reflection[1] == -1:
            self.degrees = 180 - self.degrees
        self.direction = [self.direction[0] * reflection[0], self.direction[1] * reflection[1]]

    def forward(self, distance=1):
        for i in range(distance):
            self.randomizeDegrees()
            super().forward()

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

scribe = TerminalScribe(color='green')
scribe.forward(10)
robotScribe = RobotScribe(color='yellow')
robotScribe.drawSquare(20)

canvas = CanvasAxis(40, 40, scribes=[scribe, robotScribe])

