from Vector2D import Vector2D

class Configs(object):
	"Wrapper class to contain all parameters needed to set up a simulation. Does not include the galaxy or quasar entities."
	def __init__(self, dt, dTheta, canvasDim = Vector2D(1200,1200),frameRate = 25, displayGalaxy = False, displayQuasar = False, colorQuasar = True): #Will add more in the future as it becomes relevant.
		self.dt = dt 
		self.dTheta = dTheta
		self.canvasDim = canvasDim
		self.frameRate = frameRate
		self.displayQuasar = displayQuasar
		self.displayGalaxy = displayGalaxy
		self.colorQuasar = colorQuasar


defaultConfigs = Configs(0.01,.001/625)
microConfigs = Configs(0.1,0.00001/200)
