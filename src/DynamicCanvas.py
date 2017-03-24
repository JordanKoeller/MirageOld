from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi,frameon=False,tight_layout=True)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
       # self.axes.hold(False)
        self.compute_initial_figure()
       # self.image = self.axes.imshow(filler,interpolation='nearest')
        self.filler=np.array([[random.random() for x in range(300)] for x in range(300)])
        #
        self.image = self.axes.imshow(self.filler,interpolation='nearest')

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.axes.axis('off')
        self.newData = False

    def compute_initial_figure(self):
        pass

class DynamicCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def plot(self,x,y):
        self.axes.plot(x,y)
        self.draw()

    def plotArray(self,data):
        self.image.set_data(data)
        self.draw()