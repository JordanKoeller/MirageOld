
from app.Controllers.ParametersController import ParametersController

from app.Controllers.MagMapTracerController import MagMapTracerController
from app.Controllers.QueueController import QueueController
from app.Controllers.VisualizationController import VisualizationController
from app.Preferences import GlobalPreferences


def ParametersControllerFactory(view):
    return ParametersController(view)

def VisualizationControllerFactory(view):
    return VisualizationController(view)

def TableControllerFactory(tv,pv):
    return QueueController(tv,pv)

def TracerController(view):
    return MagMapTracerController(view)

