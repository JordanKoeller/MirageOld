
from app.Controllers.ParametersController import ParametersController

from app.Controllers.QueueController import QueueController
from app.Controllers.VisualizationController import VisualizationController
from app.Controllers.LensedImageController import LensedImageController
from app.Controllers.MagMapController import MagMapController
from app.Preferences import GlobalPreferences


def ParametersControllerFactory(view):
    return ParametersController(view)

def VisualizationControllerFactory(view):
    return VisualizationController(view)

def LensedImageControllerFactory(view):
	return LensedImageController(view)

def TableControllerFactory(tv,pv):
    return QueueController(tv,pv)

def MagMapControllerFactory(view):
    return MagMapController(view)
