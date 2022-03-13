from scribes.terminalScribe import TerminalScribe

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

