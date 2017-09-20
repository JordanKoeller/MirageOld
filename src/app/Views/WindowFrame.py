from PyQt5 import uic, QtWidgets, QtCore
from .. import mainUIFile
from ..Utility.SignalRepo import SignalRepo


class WindowFrame(QtWidgets.QMainWindow, SignalRepo):
    
    playSignal = QtCore.pyqtSignal()
    pauseSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    deactivateSignal = QtCore.pyqtSignal()
    recordSignal = QtCore.pyqtSignal()
    progressDialogSignal = QtCore.pyqtSignal(int, int, str)
    progressLabelSignal = QtCore.pyqtSignal(str)
    
    
    def __init__(self, area=None,parent=None):
        super(WindowFrame, self).__init__()
        uic.loadUi(mainUIFile, self)
        self.addSignals(progressLabel=self.progressLabelSignal,
                        play=self.playSignal,
                        pause=self.pauseSignal,
                        reset=self.resetSignal,
                        progressDialog=self.progressDialogSignal
                        )
        self.setCenter(area)
        self.isAnimating = False
        
        
    def _mkStatusBar(self):
        playPauseButton = QtWidgets.QPushButton("Play/Pause")
        playPauseButton.clicked.connect(self.playSignal.emit)
        resetButton = QtWidgets.QPushButton("Reset")
        resetButton.clicked.connect(self.resetSignal.emit)
        statusLabel = QtWidgets.QLabel()
        self.statusBar.addWidget(playPauseButton)
        self.statusBar.addWidget(resetButton)
        self.statusBar.addWidget(statusLabel)
        
    
        
        
    def setCenter(self,area):
        if area:
            self.gridLayout_10.addWidget(area)
            