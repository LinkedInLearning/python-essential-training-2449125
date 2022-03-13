from scribes.terminalScribe import TerminalScribe

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

    def fromDict(data, g):
        scribe = g[data.get('classname')](
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