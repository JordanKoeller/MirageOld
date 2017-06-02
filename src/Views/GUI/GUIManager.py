'''
Created on May 31, 2017

@author: jkoeller
'''

from PyQt5 import QtWidgets, uic, QtCore, QtGui

from Views.GUI import GUIModule


class GUIMain(GUIModule, QtWidgets.QMainWindow):
    '''
    classdocs
    '''
    progress_bar_update = QtCore.pyqtSignal(int)
    progress_label_update = QtCore.pyqtSignal(str)
    sourcePos_label_update = QtCore.pyqtSignal(str)
    image_canvas_update = QtCore.pyqtSignal(object)
    curve_canvas_update = QtCore.pyqtSignal(object, object)
    progress_bar_max_update = QtCore.pyqtSignal(int)


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(GUIMain, self).__init__(parent)
        uic.loadUi('Resources/GUI/gui.ui', self)
        self.signals = self.makeSignals()
        
    def setup(self):
        pass
        
    def makeSignals(self):
        """
        Provides a list of all the created slots for UI updates and feedback.
        """
        return [self.progress_bar_update, self.progress_label_update, self.image_canvas_update,
                self.curve_canvas_update, self.progress_bar_max_update, self.sourcePos_label_update]

