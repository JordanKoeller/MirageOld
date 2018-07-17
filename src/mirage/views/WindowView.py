'''
Created on Dec 21, 2017

@author: jkoeller
'''

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea

from mirage import mainUIFile
from mirage.utility.SignalRepo import SignalRepo


class WindowView(QMainWindow, SignalRepo):
    '''
    classdocs
    '''
    
    _viewDestroyed = pyqtSignal(bool)
    _removeView = pyqtSignal(object)
    _exitSignal = pyqtSignal(bool)
    _plot_pane = pyqtSignal(bool)
    _mm_pane = pyqtSignal(bool)
    _param_pane = pyqtSignal(bool,bool)
    _image_pane = pyqtSignal(bool)
    _table_pane = pyqtSignal(bool)
    _destroy_all = pyqtSignal()
    _scale_magMap = pyqtSignal(str)
    _msg = pyqtSignal(str)
    _cmsg = pyqtSignal()
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        QMainWindow.__init__(self, *args, **kwargs)
        SignalRepo.__init__(self)
        uic.loadUi(mainUIFile, self)
        self.perspectiveManager = PerspectiveManager(self)
        self.dockArea = DockArea()
        self.splitter.addWidget(self.dockArea)
        self.actionPlotPane.toggled.connect(lambda: self.getPerspective().showPlot())
        self.actionMagMapPane.toggled.connect(lambda: self.getPerspective().showMagMap())
        self.actionParametersPane.toggled.connect(lambda: self.getPerspective().showParameters())
        self.actionImagePane.toggled.connect(lambda: self.getPerspective().showImage())
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
                        to_table_perspective = self.actionTablePerspective.triggered,
                        destroy_all = self._destroy_all,
                        scale_mag_map = self._scale_magMap,
                        message=self._msg,
                        clear_message = self._cmsg)
        self.perspectiveManager.showPerspective(True)
        self.bind_menubar_signals()

    def message_slot(self,msg):
        self.statusBar.showMessage(msg)
        
    def setPerspective(self,Perspective):
        self.signals['destroy_all'].emit()
        self.perspectiveManager.clearMenu()
        self.perspectiveManager = Perspective(self, auto_configure = True)
    
    def getPerspective(self):
        return self.perspectiveManager
        
    def bind_menubar_signals(self):
        self.actionExplorePerspective.triggered.connect(lambda: self.setPerspective(ExplorePerspectiveManager))
        self.actionTablePerspective.triggered.connect(lambda: self.setPerspective(TablePerspectiveManager))
        self.actionAnalysisPerspective.triggered.connect(lambda: self.setPerspective(AnalysisPerspectiveManager))
        self.signals['message'].connect(self.message_slot)
        self.signals['clear_message'].connect(self.statusBar.clearMessage)
        
    def removeView(self,ViewType):
        dock = None
        docks = self.dockArea.findAll()[1]
        for d in docks.values():
            if isinstance(d,ViewType):
                dock = d
        if dock:
            dock.close()
        else:
            pass
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
        self.menuExtras = []
        if auto_configure:
            self.showPerspective(True)
        
    def showParameters(self, state=True):
        self.signals['param_pane_signal'].emit(state,False)
    
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
        self.appendOptions()
        
    def addPerspectiveMenu(self,label,fn):
        item = self.v.menuModel.addAction(label)
        item.triggered.connect(fn)
        self.menuExtras.append(item)
        
    def clearMenu(self):
        for item in self.menuExtras:
            item.setVisible(False)
            item.setEnabled(False)
            item.deleteLater()
        self.menuExtras = []
        
    def appendOptions(self):
        pass

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
        self.clearMenu()

        
class ExplorePerspectiveManager(PerspectiveManager):
    
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        mainview.signals['message'].emit("Switched to explore mode.")
    
    def showPerspective(self, state=True):
        PerspectiveManager.showPerspective(self, state)
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
        self.showImage(True)

class AnalysisPerspectiveManager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        mainview.signals['message'].emit("Switched to analysis mode.")

    
    def showPerspective(self, state=True):
        PerspectiveManager.showPerspective(self, state)
        self.v.actionPlotPane.setEnabled(True)
        self.v.actionImagePane.setEnabled(True)
        self.v.actionMagMapPane.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.record_button.setEnabled(True)
        self.v.playPauseAction.setEnabled(True)
        self.v.resetAction.setEnabled(True)
        self.v.actionAnalysisPerspective.setChecked(True)
        self.v.actionParametersPane.setEnabled(True)
        self.showPlot(True)
        self.showMagMap(True)
        
    def showParameters(self, state=True):
        self.signals['param_pane_signal'].emit(state,True)
        
    def showMagMap(self, state=True):
        self.signals['mm_pane_signal'].emit(state)
        
    def appendOptions(self):
        self.addPerspectiveMenu("Logarithmic Scaling", lambda:self.signals['scale_mag_map'].emit("log10"))
        self.addPerspectiveMenu("Linear Scaling", lambda:self.signals['scale_mag_map'].emit("linear"))
        self.addPerspectiveMenu("Sqrt Scaling", lambda:self.signals['scale_mag_map'].emit("sqrt"))
        self.addPerspectiveMenu("Sinh Scaling", lambda:self.signals['scale_mag_map'].emit("sinh"))

class TablePerspectiveManager(PerspectiveManager):
    def __init__(self, mainview, auto_configure=False):
        PerspectiveManager.__init__(self, mainview, auto_configure)
        mainview.signals['message'].emit("Switched to table mode.")

    
    def showPerspective(self, state=True):
        PerspectiveManager.showPerspective(self, state)
        self.v.saveTableAction.setEnabled(True)
        self.v.loadTableAction.setEnabled(True)
        self.v.parametersEntryHelpAction.setEnabled(True)
        self.v.load_setup.setEnabled(True)
        self.v.actionTablePerspective.setChecked(True)
        self.v.signals['toggle_table_signal'].emit(True)
        self.v.signals['param_pane_signal'].emit(True,False)
        
        