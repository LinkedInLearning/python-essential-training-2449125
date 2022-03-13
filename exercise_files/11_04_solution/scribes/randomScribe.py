import random
from scribes.terminalScribe import TerminalScribe

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