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

sys.path.append(os.path.abspath('..'))

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


def load(filename=None,trial_number=None):
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

def load_simulation(filename,index=0):
    '''Convenience function for loading parameters from files. 

    
    This function accepts filenames with `.dat`, `.param`, and `.params` extensions, reads the file,
    and returns the parameters instance specified by the file. For handling files that may contain
    more than one :class:`mirage.parameters.Parameters` instance, there is an optional key-word argument to specify
    which :class:`mirage.parameters.Parameters` instance to return.
    
    Arguments:

    - `filename` (:class:`str`) : The file to parse for an inclosed :class:`mirage.parameters.Parameters` instance. Must have a `.dat`, `.params`, or `.param` file extension.
    - `index` (:class:`int`) : For files that contain more than one :class:`mirage.parameters.Parameters` instance, index specifies which version to return. (default: `0`)
    
    Returns:

        :class:`mirage.parameters.Parameters`
    '''
    if '.dat' in filename:
        return load(filename,index).parameters
    else:
        from mirage.io import ModelLoader
        loader = ModelLoader()
        loader.open(filename)
        ret = loader.load(index)
        loader.close()
        return ret

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
        Spawns and returns an instance of a :class:`mirage.Views.MagMapView`. If a model argument is supplied, will load the supplied model(s) into the view upon initialization.
        Parameters:

        - `model`: (:class:`la.Trial`,:class:`la.Experiment`, or :class:`str`) Model(s) to be loaded in upon initialization of the view. If `model` is a `str`, will assume the string is a filename which designates a `*.dat` file to load in.
        - `trial_number` (:class:`int`) : If `model` is a string specifying a `.dat` file, `trial_number` is used to specify which trial in the data file to visualize. 
    '''
    from mirage.views import WindowView, AnalysisPerspectiveManager
    from mirage.controllers import MasterController, CommandLineController
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
    # view.signals['plot_pane_signal'].emit(True)
    # view.signals['mm_pane_signal'].emit(True)
    view.show()
    return CommandLineController(model,view,controller)

def getEngineHandler(model=None):
    '''Method that returns an :class:`mirage.lens_analysis.EngineDelegate`, which provides an interface for communicating
    with a calculation engine. This method checks that an engine exists or can be constructed before returning. If no engine
    exists or can be constructed, throws an `EnvironmentError`.
    
    arguments:

    - `model` (:class:`mirage.lens_analysis.Trial` or :class:`mirage.parameters.Parameters`) : Model to be bound to the engine. The engine by default will begin calculating in the background when a model is provided. Default is `None`

    Returns:
        :class:`mirage.lens_analysis.EngineDelegate`
    '''
    if __ClusterEnabled():
        engineDel = None
        if model:
            engineDel = EngineDelegate(model)
        else:
            engineDel = EngineDelegate()
        return engineDel
    else:
        raise EnvironmentError("No cluster for building an engine could be found.")