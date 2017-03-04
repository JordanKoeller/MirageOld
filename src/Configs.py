from Vector2D import Vector2D
from Vector2D import zeroVector
import math

class Configs(object):
	"Wrapper class to contain all parameters needed to set up a simulation. Does not include the galaxy or quasar entities."
	def __init__(self, dt, dTheta, canvasDim = 800,frameRate = 25, displayGalaxy = False, displayQuasar = False, displayStars = False): #Will add more in the future as it becomes relevant.
		self.dt = dt 
		self.dTheta = dTheta
		self.canvasDim = canvasDim
		self.frameRate = frameRate
		self.displayQuasar = displayQuasar
		self.displayGalaxy = displayGalaxy
		self.displayStars = displayStars


	def enableMicrolensing(self):
		self.isMicrolensing = True
		self.displayGalaxy = False


	def disableMicrolensing(self):
		self.isMicrolensing = False

	def focusOnImage(number, shear, einsteinRadius):
		"Numbers go from top left to bottom left in a circle (clockwise)"
		self.isMicrolensing = True
		shearRotation = Vector2D(math.sin(shear.angle), -math.cos(shear.angle))



	def __str__(self):
		"Pretty print"
		return "CONFIGS\ndt = " + str(self.dt) + "\ndTheta = " + str(self.dTheta) + "\ncanvasDim = " + str(self.canvasDim) + "\n\n"
defaultConfigs = Configs(0.01,.001/625)
microConfigs = Configs(0.1,0.00001/200)
