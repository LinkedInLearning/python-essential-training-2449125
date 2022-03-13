import argparse 

# Import these so that we can pass them to "fromFile" as globals
from canvases.canvas import Canvas
from canvases.canvasAxis import CanvasAxis 
from scribes.plotScribe import PlotScribe 
from scribes.randomScribe import RandomWalkScribe
from scribes.robotScribe import RobotScribe
from scribes.terminalScribe import TerminalScribe
import scribes 

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, help='The input Scribe file to run')

args = parser.parse_args()

print(args.input)

c = Canvas.fromFile(args.input, globals())
c.go()
