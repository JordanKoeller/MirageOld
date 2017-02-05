from Vector2D import Vector2D
from Vector2D import zeroVector
import math

class Configs(object):
	"Wrapper class to contain all parameters needed to set up a simulation. Does not include the galaxy or quasar entities."
	def __init__(self, dt, dTheta, canvasDim = Vector2D(800,800),frameRate = 25, displayGalaxy = False, displayQuasar = False, colorQuasar = True, frameShift = zeroVector): #Will add more in the future as it becomes relevant.
		self.dt = dt 
		self.dTheta = dTheta
		self.canvasDim = canvasDim
		self.frameRate = frameRate
		self.displayQuasar = displayQuasar
		self.displayGalaxy = displayGalaxy
		self.colorQuasar = colorQuasar
		self.frameShift = frameShift

	def setShift(self,enabled,einsteinRadius,theta):
		if enabled:
			self.frameShift = Vector2D(-einsteinRadius*math.sin(theta),einsteinRadius*math.cos(theta),'rad')
		else:
			self.frameShift = zeroVector

defaultConfigs = Configs(0.01,.001/625)
microConfigs = Configs(0.1,0.00001/200)
