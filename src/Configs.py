from Vector2D import Vector2D
from Vector2D import zeroVector
import math
from MassFunction import MassFunction

class Configs(object):
	"Wrapper class to contain all parameters needed to set up a simulation. Does not include the galaxy or quasar entities."
	def __init__(self, dt, dTheta, canvasDim = 800,frameRate = 25, displayGalaxy = False, displayQuasar = False, displayStars = False): #Will add more in the future as it becomes relevant.
		self.dt = dt 
		self.dTheta = dTheta
		self.canvasDim = canvasDim
		self.frameRate = frameRate
		self.__displayQuasar = displayQuasar
		self.__displayGalaxy = displayGalaxy
		self.__displayStars = displayStars
		self.massGenerator = None
		self.tolerance = 0.05
		self.isMicrolensing = False

	def updateDisplay(self,displayGalaxy = None, displayQuasar = None):
		if displayGalaxy != None:
			self.__displayGalaxy = displayGalaxy
			self.__displayStars = displayGalaxy
		if displayQuasar != None:
			self.__displayQuasar = displayQuasar

	def enableMicrolensing(self):
		self.isMicrolensing = True
		self.__displayGalaxy = False


	def disableMicrolensing(self):
		self.isMicrolensing = False

	def focusOnImage(number, shear, einsteinRadius):
		"Numbers go from top left to bottom left in a circle (clockwise)"
		self.isMicrolensing = True
		shearRotation = Vector2D(math.sin(shear.angle), -math.cos(shear.angle))

	def getStarMasses(self,totalMass = None,numStars = None):
		print("total mass = " + str(totalMass))
		if totalMass != None:
			self.massGenerator = self.massGenerator or MassFunction()
			return self.massGenerator.starField(totalMass,self.tolerance)
		else:
			self.massGenerator = self.massGenerator or MassFunction()
			return self.massGenerator.query(numStars)

	@property
	def displayStars(self):
		return self.__displayStars

	@property
	def displayQuasar(self):
		return not self.isMicrolensing and self.__displayQuasar
	@property
	def displayGalaxy(self):
		return not self.isMicrolensing and self.__displayGalaxy

	def __str__(self):
		"Pretty print"
		return "CONFIGS\ndt = " + str(self.dt) + "\ndTheta = " + str(self.dTheta) + "\ncanvasDim = " + str(self.canvasDim) + "\n\n"
defaultConfigs = Configs(0.01,.001/625)
microConfigs = Configs(0.1,0.00001/200)
