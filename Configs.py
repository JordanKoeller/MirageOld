from Vector2D import Vector2D

class Configs(object):
	"Wrapper class to contain all parameters needed to set up a simulation. Does not include the galaxy or quasar entities."
	def __init__(self, dt, dTheta, canvasDim): #Will add more in the future as it becomes relevant.
		self.dt = dt 
		self.dTheta = dTheta
		self.canvasDim = canvasDim


defaultConfigs = Configs(0.01,.001/625,Vector2D(800,800))
microConfigs = Configs(0.1,0.00001/200,Vector2D(800,800))
