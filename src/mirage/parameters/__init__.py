from .Parameters import Parameters
from .ExperimentParams import ExperimentParams, MagMapParameters, \
Simulation, BatchLightCurveParameters
from .ExperimentParams import MagMapParameters

def DefaultParameters():
	from .stellar import defaultQuasar, defaultGalaxy
	from mirage.utility import PixelRegion, Vector2D
	region = PixelRegion(Vector2D(0,0,'arcsec'),Vector2D(40,40,'arcsec'),Vector2D(2000,2000))
	return Parameters(defaultGalaxy,defaultQuasar,region)
