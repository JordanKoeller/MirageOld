# %gui qt5

import sys

from .AbstractFileWrapper import AbstractFileWrapper
from .DirectoryMap import DirectoryMap
from .Experiment import Experiment
from .Trial import Trial
from ._environ import requiresGUI



def load(filename='Untitled.dat'):
    if filename is None:
        from PyQt5 import QtWidgets
        filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.dat')[0]
    if filename:
        lngth = len(filename)
        if filename[lngth-4::] == '.dat':
            return Experiment(filename)
        else:
            return DirectoryMap(filename)
    else:
        return None
def describe(filename):
    if isinstance(filename, str):
        tmp = load(filename)
        tmp.describe
    elif isinstance(filename, AbstractFileWrapper):
            filename.describe
    else:
        raise ValueError("argument must be a filename or AbstractFileWrapper subtype.")

# def traceQuasar(expt,trialNum=0):
#     from PyQt5 import QtWidgets
#     from ..Views.GUI.GUITracerWindow import GUITracerWindow
#     app = QtWidgets.QApplication(sys.argv)
#     if isinstance(expt,str):
#         ui = GUITracerWindow(expt,trialNum=trialNum)
#         ui.show()
#     else:
#         ui = GUITracerWindow(expt.file.name,expt.trialNumber)
#         ui.show()
#     app.exec_()
# 
# def explore(expt):
#     params = None
#     if isinstance(expt,AbstractFileWrapper):
#         params = expt.parameters
#     elif isinstance(expt, Parameters):
#         params = expt
#     else:
#         raise ValueError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
#         return
#     if not params:
#         return ValueError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
#         return
#     try:
#         ui = GUIManager()
#         ui.switchToVisualizing()
#         ui.bindFields(params)
#         ui.switchToVisualizing()
#         ui.show()
#     except:
#         raise EnvironmentError("Must have a Qt event loop running. If you are in ipython, execute the command '%gui qt5' then try again.")

@requiresGUI
def visualizeMagMap(model=None):
    '''
        Spawns and returns an instance of a `app.Views.MagMapView`. If a model argument is supplied,
        will load the supplied model(s) into the view upon initialization.

        Parameters:

        - `model`: (`lens_analysis.Trial`,`lens_analysis.Experiment`, or `str`) Model(s) to be loaded in upon
        initialization of the view. If `model` is a `str`, will assume the string is a filename which
        designates a `*.dat` file to load in.
    '''
    from app.Views.MainView import MainView
    from app.Views.MagMapView import MagMapView
    view = MainView()
    mmt = MagMapView(title = "Figure 1")
    view.addView(mmt)
    view.show()
    return view
    if isinstance(model,Trial): 
        mm = model.getMagMap()
        view.setMagMap(mm,0)
    elif isinstance(model,Experiment):
        for i in model:
            mm = i.getMagMap()
            view.setMagMap(mm,0)
    elif isinstance(model,str):
        print("Yeah personal best")
    else:
        raise ValueError("model must be of type lens_analysis.Trial, lens_analysis.Experiment, or a filename")
    return view