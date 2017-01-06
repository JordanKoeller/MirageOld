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
from matplotlib.patches import Circle

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    "For Internal Use only."
    def __init__(self, parent=None, width=8, height=8, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi,frameon=False,tight_layout=True)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        self.filler=np.array([[random.random() for x in range(500)] for x in range(500)])
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
    "A Matplotlib figure canvas embedded in a Qt graphicsView. Allows use of MPL library in a GUI setting."
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
    def compute_initial_figure(self):
        "Renders initial image to be displayed"
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
    def plotArray(self,byteArray):
        "Takes the passed in byteArray of RGB values and displays it to the screen as an image."
        # //print(byteArray.dtype)
        self.image.set_data(byteArray)
        self.draw()
        # self.axes.add_patch(Circle((250,250),5,color="#ee321c"))
    def drawCircle(self,cCenter,cRadius,cColor,circle = None):
        if circle is None:
            circle = Circle((cCenter.x+250,cCenter.y+250),cRadius,color = cColor)
        self.axes.add_patch(circle)
        

