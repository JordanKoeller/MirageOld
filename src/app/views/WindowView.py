'''
Created on Dec 21, 2017

@author: jkoeller
'''

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea

from app import mainUIFile
from app.utility.SignalRepo import SignalRepo


class WindowView(QMainWindow, SignalRepo):
    '''
    classdocs
    '''
    
    _viewDestroyed = pyqtSignal(bool)
    _removeView = pyqtSignal(object)
    _exitSignal = pyqtSignal(bool)
    _plot_pane = pyqtSignal(bool)
    _mm_pane = pyqtSignal(bool)
    _param_pane = pyqtSignal(bool)
    _image_pane = pyqtSignal(bool)
    _table_pane = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        QMainWindow.__init__(self, *args, **kwargs)
        SignalRepo.__init__(self)
        uic.loadUi(mainUIFile, self)
        self.perspectiveManager = PerspectiveManager(self)
        self.perspectiveManager.showPerspective(True)
        self.dockArea = DockArea()
        self.gridLayout_10.addWidget(self.dockArea)
        self.actionPlotPane.toggled.connect(self.perspectiveManager.showPlot)
        self.actionMagMapPane.toggled.connect(self.perspectiveManager.showMagMap)
        self.actionParametersPane.toggled.connect(self.perspectiveManager.showParameters)
        self.actionImagePane.toggled.connect(self.perspectiveManager.showImage)
        self._removeView.connect(self.removeView)
        self.addSignals(exit_signal = self.shutdown.triggered,
                        play_signal = self.playPauseAction.triggered,
                        reset_signal = self.resetAction.triggered,
                        save_table = self.saveTableAction.triggered,
                        load_table = self.loadTableAction.triggered,
                        save_setup = self.save_setup.triggered,
                        load_setup = self.load_setup.triggered,
                        record_signal = self.record_button.triggered,
                        plot_pane_signal = self._plot_pane,
                        mm_pane_signal = self._mm_pane,
                        param_pane_signal = self._param_pane,
                        image_pane_signal = self._image_pane,
                        remove_view = self._removeView,
                        toggle_table_signal = self._table_pane,
                        to_analysis_perspective = self.actionAnalysisPerspective.triggered,
                        to_explore_perspective = self.actionExplorePerspective.triggered,
                        to_table_perspective = self.actionTablePerspective.triggered)
        self.bind_menubar_signals()
        
    def setPerspective(self,Perspective):
        print("Setting Perspective to " + str(Perspective))
        self.dockArea.clear()
        self.perspective = Perspective(self, auto_configure = True)
        
    def bind_menubar_signals(self):
        self.actionExplorePerspective.triggered.connect(lambda: self.setPerspective(ExplorePerspectiveManager))
        self.actionTablePerspective.triggered.connect(lambda: self.setPerspective(TablePerspectiveManager))
        self.actionAnalysisPerspective.triggered.connect(lambda: self.setPerspective(AnalysisPerspectiveManager))
        
    def removeView(self,ViewType):
        dock = None
        docks = self.dockArea.findAll()[1]
        for d in docks.values():
            if isinstance(d,ViewType):
                dock = d
        if dock:
            dock.close()
        else:
            print("Could not find a " + str(ViewType))
            print(docks.values())
            
    def addView(self,view):
        assert isinstance(view,Dock)
        self.dockArea.addDock(view)
    

class PerspectiveManager(object):
    '''
    Abstract class for handling perspective-specific GUI things. 
    '''
    
    def __init__(self, mainview, auto_configure=False):
        self.v = mainview
        self.signals = self.v.signals
        if auto_configure:
            self.showPerspective(True)
        
    def showParameters(self, state=True):
        self.signals['param_pane_signal'].emit(state)
    
    def showTable(self, state=True):
        print("Need to bind for making a tableview")

    def showImage(self, state=True):
        self.signals['image_pane_signal'].emit(state)

    def showPlot(self, state=True):
        self.signals['plot_pane_signal'].emit(state)

    def showMagMap(self, state=True):
        self.signals['mm_pane_signal'].emit(state)
    
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
        self.v.actionExplorePerspective.setChecked(False)
        self.v.actionAnalysisPerspective.setChecked(False)
        self.v.actionAnalysisPerspective.setChecked(False)
        
class ExplorePerspectiveManager(PerspectiveManager):
    
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
    
#     def showParameters(self, state=True):
#         pass
#     
#     def showTable(self, state=True):
#         pass
# 
#     def showImage(self, state=True):
#         pass
# 
#     def showPlot(self, state=True):
#         pass
# 
#     def showMagMap(self, state=True):
#         pass
    
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
        self.v.actionExplorePerspective.setChecked(True)

class AnalysisPerspectiveManager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        
#     def showParameters(self, state=True):
#         pass
#     
#     def showTable(self, state=True):
#         pass
# 
#     def showImage(self, state=True):
#         pass
# 
#     def showPlot(self, state=True):
#         pass
# 
#     def showMagMap(self, state=True):
#         pass
    
    def showPerspective(self, state=True):
        self._disableMenuBar()
        self.v.actionPlotPane.setEnabled(True)
        self.v.actionImagePane.setEnabled(True)
        self.v.actionMagMapPane.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.record_button.setEnabled(True)
        self.v.playPauseAction.setEnabled(True)
        self.v.resetAction.setEnabled(True)
        self.v.actionAnalysisPerspective.setChecked(True)

class TablePerspectiveManager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        
#     def showParameters(self, state=True):
#         pass
#     
#     def showTable(self, state=True):
#         pass
# 
#     def showImage(self, state=True):
#         pass
# 
#     def showPlot(self, state=True):
#         pass
# 
#     def showMagMap(self, state=True):
#         pass
    
    def showPerspective(self, state=True):
        self._disableMenuBar()
        self.v.saveTableAction.setEnabled(True)
        self.v.loadTableAction.setEnabled(True)
        self.v.parametersEntryHelpAction.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.actionTablePerspective.setChecked(True)
        self.v.signals['toggle_table_signal'].emit(True)
        self.v.signals['param_pane_signal'].emit(True)