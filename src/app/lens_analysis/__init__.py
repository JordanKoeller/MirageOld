import numpy as np
import copy
import glob
import os
import sys

from .AbstractFileWrapper import AbstractFileWrapper
from .DirectoryMap import DirectoryMap
from .Experiment import Experiment
from .Trial import Trial
from .EngineDelegate import EngineDelegate
# from .TrialWithEngine import TrialWithEngine

sys.path.append(os.path.abspath('..'))

_with_engine = False


def enable_engine(*args,**kwargs):
    global _with_engine
    _with_engine = True

def __EventLoopActive():
    from PyQt5 import QtWidgets
    if QtWidgets.QApplication.instance():
        return True
    else:
        return False

def __ClusterEnabled():
    try:
        from pyspark.context import SparkContext
        if SparkContext._active_spark_context:
            return True 
        else:
            return False
    except:
        return False

def _requiresGUI(fn):
    def decorator(*args,**kwargs):
        if __EventLoopActive():
            return fn(*args,**kwargs)
        else:
            print("Must have Qt5 Event Loop initialized. To initialize, run the command \n\n>>> %gui qt5 \n\n")
    setattr(decorator,'__doc__',getattr(fn,'__doc__'))
    return decorator


def load(filename='Untitled.dat',trial_number=None,with_engine = False):
    '''
    Given a filename, returns a :class:`la.Experiment` (if a `.dat` file is provided) or a :class:`la.DirectoryMap`
    (if a directory name is provided) instance generated from the specified file. If filename is None, and a Qt event loop 
    is running, opens a file dialog to specify the file.

    Parameters:
    
    - `filename` (:class:`str`) : Filename to look up. Defaults to '`Untitled.dat`'. If None is passed in, opens a dialog to specify the file.
    - 'trial' (:class:`int`) : If `filename` specifies a file, then specifying a trial number will cause this method to return the specified :class:`Trial` instance from the data file described.
    
    Returns:
    
    - :class:`Directory` if the `filename` argument is a directory.
    - :class:`Experiment` if the `filename` argument is a `.dat` file and no `trial_number` is given.
    - :class:`Trial` if the `filename` argument is a `.dat` file, and a `trial_number` is given.
    '''
    if filename is None:
        from PyQt5 import QtWidgets
        filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.dat')[0]
    if filename:
        lngth = len(filename)
        if filename[lngth-4::] == '.dat':
            ret = Experiment(filename)
            if trial_number != None:
                ret = ret[trial_number]
            return ret
        else:
            return DirectoryMap(filename)
    else:
        return None

def describe(filename):
    '''
    Convenience function for getting information about a file.

    Given a `.dat` filename, prints the file's description. This method is equivalent to calling:

    >>> import lens_analysis as la
    >>> data_to_describe = la.load('file.dat')
    >>> data_to_describe.describe

    Parameters: `filename` (:class:`str`) : The data file to describe. Must have a `.dat` extension. Also accepts any subtype of :class:`la.AbstractFileWrapper`.
    '''
    if isinstance(filename, str) and filename[len(filename)-4::] == '.dat':
        tmp = load(filename)
        tmp.describe
    elif isinstance(filename, AbstractFileWrapper):
            filename.describe
    else:
        raise ValueError("argument must be a filename or AbstractFileWrapper subtype.")

@_requiresGUI
def visualizeMagMap(model=None,trial_number=None, with_engine = False):
    '''
        Spawns and returns an instance of a :class:`app.Views.MagMapView`. If a model argument is supplied, will load the supplied model(s) into the view upon initialization.
        Parameters:

        - `model`: (:class:`la.Trial`,:class:`la.Experiment`, or :class:`str`) Model(s) to be loaded in upon initialization of the view. If `model` is a `str`, will assume the string is a filename which designates a `*.dat` file to load in.
        - `trial_number` (:class:`int`) : If `model` is a string specifying a `.dat` file, `trial_number` is used to specify which trial in the data file to visualize. 
    '''
    from app.views import WindowView, AnalysisPerspectiveManager
    from app.controllers import MasterController, CommandLineController
    view = WindowView()
    controller = MasterController()
    controller.bind_view_signals(view)
    if isinstance(model,str):
        model = load(model,trial_number)
    elif isinstance(model,Experiment):
        model = model[trial_number]
    elif isinstance(model,Trial):
        pass
    else:
        raise ValueError("model must be a lens_analysis.Trial, lens_analysis.Experiment, or str instance.")
#     view.signals['to_analysis_perspective'].emit()
    controller.enableAnalysis(model)
    view.setPerspective(AnalysisPerspectiveManager)
    view.signals['plot_pane_signal'].emit(True)
    view.signals['mm_pane_signal'].emit(True)
    view.show()
    return CommandLineController(model,view,controller)

def getEngineHandler(model=None):
    engineDel = None
    if model:
        engineDel = EngineDelegate(model.parameters)
    else:
        engineDel = EngineDelegate()
    return engineDel