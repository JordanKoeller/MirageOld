
from app.Controllers.ParametersController import ParametersController

from app.Controllers.MagMapTracerController import MagMapTracerController
from app.Controllers.QueueController import QueueController
from app.Controllers.VisualizationController import VisualizationController
from ._PreferencesParser import globalPreferences


def _ParametersControllerFactory(view):
    return ParametersController(view)

def _VisualizationControllerFactory(view):
    return VisualizationController(view)

def _ExperimentTableController(view):
    return QueueController(view)

def _TracerController(view):
    return MagMapTracerController(view)