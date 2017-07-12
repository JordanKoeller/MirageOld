# %gui qt5

from lens_analysis.AbstractFileWrapper import AbstractFileWrapper
from lens_analysis.DirectoryMap import DirectoryMap
from lens_analysis.Experiment import Experiment
from lens_analysis.Trial import Trial
from ..Views.GUI.GUIManager import GUIManager
from ..Models.Parameters.Parameters import Parameters
from ..Models.Parameters.ExperimentParams import ResultTypes
from ..Controllers.FileManagers.TableFileManager import TableFileManager
from ..Controllers.Threads.QueueThread import QueueThread
from ..Controllers.FileManagers import QueueFileManager
from ..Utility.NullSignal import NullSignal


def load(filename):
    lngth = len(filename)
    if filename[lngth-4::] == '.dat':
        return Experiment(filename)
    else:
        return DirectoryMap(filename)

def describe(filename):
    if isinstance(filename, str):
        tmp = load(filename)
        tmp.describe
    elif isinstance(filename, AbstractFileWrapper):
            filename.describe
    else:
        raise ValueError("argument must be a filename or AbstractFileWrapper subtype.")


def explore(expt):
    params = None
    if isinstance(expt,AbstractFileWrapper):
        params = expt.parameters
    elif isinstance(expt, Parameters):
        params = expt
    else:
        raise ValueError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
        return
    if not params:
        returneError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
        return
    try:
        ui = GUIManager()
        ui.switchToVisualizing()
        ui.bindFields(params)
        ui.switchToVisualizing()
        ui.show()
    except:
        raise EnvironmentError("Must have a Qt event loop running. If you are in ipython, execute the command '%gui qt5' then try again.")
