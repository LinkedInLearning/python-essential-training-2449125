import os
import time
from termcolor import colored
import math 
import random

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
        self._canvas[round(pos[0])][round(pos[1])] = mark

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

        print(' '.join([self.formatAxisNumber(x) for x in range(self._x)]))

class TerminalScribe:
    def __init__(self, canvas, color='red', mark='*', trail='.', pos=(0, 0), framerate=.05, direction=[0, 1]):
        self.canvas = canvas
        self.trail = trail
        self.mark = mark
        self.framerate = framerate
        self.pos = pos
        self.color=color
        self.direction = direction

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


canvas = CanvasAxis(30, 30)
plotScribe = PlotScribe(canvas)
plotScribe.plotX(sine)

robotScribe = RobotScribe(canvas, color='blue')
robotScribe.drawSquare(10)

randomScribe = RandomWalkScribe(canvas, color='green', pos=(0, 0))
randomScribe.forward(1000)



