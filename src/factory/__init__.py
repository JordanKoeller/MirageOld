
from app.Controllers.ParametersController import ParametersController

from app.Controllers.MagMapTracerController import MagMapTracerController
from app.Controllers.QueueController import QueueController
from app.Controllers.VisualizationController import VisualizationController
<<<<<<< HEAD
from ._PreferencesParser import globalPreferences


def _ParametersControllerFactory(view):
    return ParametersController(view)

def _VisualizationControllerFactory(view):
    return VisualizationController(view)

def _ExperimentTableController(view):
    return QueueController(view)

def _TracerController(view):
    return MagMapTracerController(view)
=======
from app.Preferences import GlobalPreferences


def ParametersControllerFactory(view):
    return ParametersController(view)

def VisualizationControllerFactory(view):
    return VisualizationController(view)

def TableControllerFactory(tv,pv):
    return QueueController(tv,pv)

def TracerController(view):
    return MagMapTracerController(view)

>>>>>>> 491e7782492888a33860c98eeb114680b089ab82
