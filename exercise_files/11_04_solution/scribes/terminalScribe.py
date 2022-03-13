from termcolor import colored, COLORS
import math 
from inspect import getmembers, ismethod

from errors import InvalidParameter 
from utils import is_number 


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

    def fromDict(data, g):
        scribe = g[data.get('classname')](
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