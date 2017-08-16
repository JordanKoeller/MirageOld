# %gui qt5

import sys


# from ..Controllers.FileManagers import QueueFileManager
# from ..Controllers.FileManagers.TableFileManager import TableFileManager
# from ..Controllers.Threads.QueueThread import QueueThread
# from ..Models.Parameters.ExperimentParams import ResultTypes
# from ..Models.Parameters.Parameters import Parameters
# from ..Utility.NullSignal import NullSignal
# from ..Views.GUI.GUIManager import GUIManager
from .AbstractFileWrapper import AbstractFileWrapper
from .DirectoryMap import DirectoryMap
from .Experiment import Experiment
from .Trial import Trial


def load(filename='Untitled.dat'):
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

print("Finished loading")