from PyQt5 import QtCore, QtGui, QtWidgets
from Engine_cl import Engine_cl
from Configs import Configs
from stellar import Galaxy
from stellar import Quasar
from stellar import defaultGalaxy
from stellar import defaultQuasar
from Configs import defaultConfigs
from stellar import microGalaxy
from stellar import microQuasar
from Configs import microConfigs
import threading as par
from Vector2D import Vector2D
from enum import Enum
from window import Ui_MainWindow
import time

class CanvasType(Enum):
    LABEL_CANVAS = 0
    MPL_CANVAS = 1
    NONE_TYPE = 2

class SimThread(QtCore.QThread):
    def __init__(self,engine,labelCanvas = None, mplCanvas = None):
        QtCore.QThread.__init__(self)
        self.engine = engine 
        self.calculating = False
        self.reconfiguring = False


    def setCanvas(self,canvas, canvasType = CanvasType.LABEL_CANVAS):
        self.canvas = canvas

    def run(self):
        self.canvas.setPixmap(QtGui.QPixmap.fromImage(self.engine.img))
        if self.engine.needsReconfiguring:
            self.reconfiguring = True
            self.engine.reconfigure()
            self.reconfiguring = False
        if not self.reconfiguring:
            self.calculating = True
            interval = 1/self.engine.configs.frameRate
            while self.calculating:
                timer = time.clock()
                frame = self.engine.drawFrame()
                self.canvas.pixmap().convertFromImage(frame)
                self.canvas.update()
                deltaT = timer.clock() - timer
                if deltaT < interval:
                    time.sleep(interval-deltaT)
                else:
                    print("No sleep on frame " + str(counter))






def launch():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

