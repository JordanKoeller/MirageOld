'''
Created on Dec 21, 2017

@author: jkoeller
'''

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph.dockarea.DockArea import DockArea

from app import mainUIFile
from app.utility.SignalRepo import SignalRepo

from PyQt5.QtCore import pyqtSignal

class WindowView(QMainWindow, SignalRepo):
    '''
    classdocs
    '''
    
    _viewDestroyed = pyqtSignal(object)
    _exitSignal = pyqtSignal(object)


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        QMainWindow.__init__(self, *args, **kwargs)
        SignalRepo.__init__(self)
        uic.loadUi(mainUIFile, self)
        self.perspectiveManager = PerspectiveManager(self)
        self.perspectiveManager.showPerspective(True)
        self.actionExplorePerspective.triggered.connect(lambda: self.setPerspective(ExplorePerspectiveManager))
        self.actionTablePerspective.triggered.connect(lambda: self.setPerspective(TablePerspectivemanager))
        self.actionAnalysisPerspective.triggered.connect(lambda: self.setPerspective(AnalysisPerspectiveManager))
        self.dockArea = DockArea()
        self.gridLayout_10.addWidget(self.dockArea)
        self.addSignals(view_destroyed = self._viewDestroyed,
                        exit_signal = self._exitSignal)
        
    def setPerspective(self,Perspective):
        self.perspective = Perspective(self, auto_configure = True)
        
#     def addController(self, controller):
#         '''
#         Adds a :class:`app.views.View` to the window. 
#         '''
#         assert isinstance(controller, Controller)
#         controller.bind_to_model(self.modelRef)
#         view = controller.spawn_view()
#         view.signals['view_closed'].connect(lambda: self.removeController(controller))
#         self.dockArea.addDock(view)
#         self._controllers.append(controller)
#         
#     def removeController(self, controller):
#         assert isinstance(controller, Controller)
#         self._controllers.remove(controller)
        
    @property
    def modelRef(self):
        pass

class PerspectiveManager(object):
    '''
    Abstract class for handling perspective-specific GUI things. 
    '''
    
    def __init__(self, mainview, auto_configure=False):
        self.v = mainview
        if auto_configure:
            self.showPerspective(True)
        
    def showParameters(self, state=True):
        pass
    
    def showTable(self, state=True):
        pass

    def showImage(self, state=True):
        pass

    def showPlot(self, state=True):
        pass

    def showMagMap(self, state=True):
        pass
    
    def showPerspective(self, state=True):
        self._disableMenuBar()
    

    def _disableMenuBar(self):
        self.v.saveTableAction.setDisabled(True)
        self.v.loadTableAction.setDisabled(True)
        self.v.parametersEntryHelpAction.setDisabled(True)
        self.v.actionPlotPane.setDisabled(True)
        self.v.actionImagePane.setDisabled(True)
        self.v.actionMagMapPane.setDisabled(True)
        self.v.actionParametersPane.setDisabled(True)
        self.v.actionExport.setDisabled(True)
        self.v.load_setup.setDisabled(True)
        self.v.save_setup.setDisabled(True)
        self.v.record_button.setDisabled(True)
        self.v.actionDEPRECATED.setDisabled(True)
        self.v.playPauseAction.setDisabled(True)
        self.v.resetAction.setDisabled(True)
        
class ExplorePerspectiveManager(PerspectiveManager):
    
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
    
    def showParameters(self, state=True):
        pass
    
    def showTable(self, state=True):
        pass

    def showImage(self, state=True):
        pass

    def showPlot(self, state=True):
        pass

    def showMagMap(self, state=True):
        pass
    
    def showPerspective(self, state=True):
        self._disableMenuBar()
        self.v.parametersEntryHelpAction.setEnabled(True)
        self.v.actionPlotPane.setEnabled(True)
        self.v.actionImagePane.setEnabled(True)
        self.v.actionParametersPane.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.save_setup.setEnabled(True)
        self.v.record_button.setEnabled(True)
        self.v.playPauseAction.setEnabled(True)
        self.v.resetAction.setEnabled(True)

class AnalysisPerspectiveManager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        
    def showParameters(self, state=True):
        pass
    
    def showTable(self, state=True):
        pass

    def showImage(self, state=True):
        pass

    def showPlot(self, state=True):
        pass

    def showMagMap(self, state=True):
        pass
    
    def showPerspective(self, state=True):
        self.v.actionPlotPane.setEnabled(True)
        self.v.actionImagePane.setEnabled(True)
        self.v.actionMagMapPane.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.record_button.setEnabled(True)
        self.v.playPauseAction.setEnabled(True)
        self.v.resetAction.setEnabled(True)

class TablePerspectivemanager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        
    def showParameters(self, state=True):
        pass
    
    def showTable(self, state=True):
        pass

    def showImage(self, state=True):
        pass

    def showPlot(self, state=True):
        pass

    def showMagMap(self, state=True):
        pass
    
    def showPerspective(self, state=True):
        self.v.saveTableAction.setEnabled(True)
        self.v.loadTableAction.setEnabled(True)
        self.v.parametersEntryHelpAction.setEnabled(True)
        self.v.load_setup.setEnabled(True)
