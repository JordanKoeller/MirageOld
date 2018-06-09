'''
Module for analyzing data produced by lensing_simulator. 

Contains decorator classes for file objects for fetching data.

The class :class:`Trial` contains most of the functionality for fetching data from a trial. Features include:
  - Fetching of a :class:`Parameters <app.Parameters.Parameters>` instance for how the simulation was set up.
  - Plotting of a magnification map with a :class:`MagMapView <app.Views.MagMapView.MagMapView>` view.
  - Fetching a light curve from the simulation or magnification map data.
  - Generating a FITS file from magnification map data.
  - Histogram of pixel values from magnification map data.

Below is an example of how to use the module for getting a magnification map as a FITS file.

>>> import lens_analysis as la
# Create a Experiment class instance, wrapping 'filename.dat'
>>> data = la.load('filename.dat') 
# Fetch the first trial in the file as a Trial instance.
>>> trial1 = data[0]
# Save the trial's magnification map to a FITS file
>>> trial1.getFitsFile('filename.fits')

 
'''

import numpy as np
import copy
import glob
import os
import sys

from .parameters.ExperimentParams import LightCurveParameters, \
    MagMapParameters, StarFieldData, BatchLightCurveParameters
from .calculator.ExperimentResultCalculator import varyTrial


sys.path.append(os.path.abspath('.'))



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


def _requiresDtype(dtype):
    def decorator(fn):
        def decorated(self,*args,**kwargs):
            for k,v in self._exptTypes.items():
                if isinstance(k, dtype):
                    index = v
                    return fn(self,index,*args,**kwargs)
            raise AttributeError("Trial does not contain "+str(dtype) +" data.")
        setattr(decorated,'__doc__',getattr(fn, '__doc__'))
        return decorated
    return decorator

def _requiresCalculationEngine(fn):
    def decorator(*args,**kwargs):
        if __ClusterEnabled():
            return fn(*args,**kwargs)
        else:
            s1 = "ERROR: This method requres a pyspark session be active with cluster communication."
            s2 = "Please restart your REPL from the lens_analysis.sh script or create a SParkContext through pyspark."
            raise AttributeError(s1 + "\n" + s2)
    setattr(decorator,'__doc__',getattr(fn,'__doc__'))
    return decorator





        
    
        














# def load(filename='Untitled.dat',trial_number=None):
#     '''
#     Given a filename, returns a :class:`la.Experiment` (if a `.dat` file is provided) or a :class:`la.DirectoryMap`
#     (if a directory name is provided) instance generated from the specified file. If filename is None, and a Qt event loop 
#     is running, opens a file dialog to specify the file.

#     Parameters:
    
#     - `filename` (:class:`str`) : Filename to look up. Defaults to '`Untitled.dat`'. If None is passed in, opens a dialog to specify the file.
#     - 'trial' (:class:`int`) : If `filename` specifies a file, then specifying a trial number will cause this method to return the specified :class:`Trial` instance from the data file described.
    
#     Returns:
    
#     - :class:`Directory` if the `filename` argument is a directory.
#     - :class:`Experiment` if the `filename` argument is a `.dat` file and no `trial_number` is given.
#     - :class:`Trial` if the `filename` argument is a `.dat` file, and a `trial_number` is given.
#     '''
#     if filename is None:
#         from PyQt5 import QtWidgets
#         filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.dat')[0]
#     if filename:
#         lngth = len(filename)
#         if filename[lngth-4::] == '.dat':
#             ret = Experiment(filename)
#             if trial_number != None:
#                 ret = ret[trial_number]
#             return ret
#         else:
#             return DirectoryMap(filename)
#     else:
#         return None

# def describe(filename):
#     '''
#     Convenience function for getting information about a file.

#     Given a `.dat` filename, prints the file's description. This method is equivalent to calling:

#     >>> import lens_analysis as la
#     >>> data_to_describe = la.load('file.dat')
#     >>> data_to_describe.describe

#     Parameters: `filename` (:class:`str`) : The data file to describe. Must have a `.dat` extension. Also accepts any subtype of :class:`la.AbstractFileWrapper`.
#     '''
#     if isinstance(filename, str) and filename[len(filename)-4::] == '.dat':
#         tmp = load(filename)
#         tmp.describe
#     elif isinstance(filename, AbstractFileWrapper):
#             filename.describe
#     else:
#         raise ValueError("argument must be a filename or AbstractFileWrapper subtype.")

# @_requiresGUI
# def visualizeMagMap(model=None,trial_number=None):
#     '''
#         Spawns and returns an instance of a :class:`app.Views.MagMapView`. If a model argument is supplied, will load the supplied model(s) into the view upon initialization.
#         Parameters:

#         - `model`: (:class:`la.Trial`,:class:`la.Experiment`, or :class:`str`) Model(s) to be loaded in upon initialization of the view. If `model` is a `str`, will assume the string is a filename which designates a `*.dat` file to load in.
#         - `trial_number` (:class:`int`) : If `model` is a string specifying a `.dat` file, `trial_number` is used to specify which trial in the data file to visualize. 
#     '''
#     from app.views import WindowView, AnalysisPerspectiveManager
#     from app.controllers import MasterController, CommandLineController
#     view = WindowView()
#     controller = MasterController()
#     controller.bind_view_signals(view)
#     if isinstance(model,str):
#         model = load(model,trial_number)
#     elif isinstance(model,Experiment):
#         model = model[trial_number]
#     elif isinstance(model,Trial):
#         pass
#     else:
#         raise ValueError("model must be a lens_analysis.Trial, lens_analysis.Experiment, or str instance.")
# #     view.signals['to_analysis_perspective'].emit()
#     controller.enableAnalysis(model)
#     view.setPerspective(AnalysisPerspectiveManager)
#     view.signals['plot_pane_signal'].emit(True)
#     view.signals['mm_pane_signal'].emit(True)
#     view.show()
#     return CommandLineController(model,view,controller)

