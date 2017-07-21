from pyqtgraph import QtCore, QtGui
from ...Utility.NullSignal import NullSignal
cimport numpy as np
import numpy as np
import math 
from ...Models.Model import Model
from .Drawer cimport Drawer

cdef class CurveDrawer_Tracer(Drawer):

    def __init__(self,signal=NullSignal):
        Drawer.__init__(self,signal)
        self.reset()

    cdef append(self, double y, double x=-1):
        # print(y)
        cdef np.ndarray[np.float64_t, ndim=1] replaceX = np.ndarray((self.index+1),dtype=np.float64)
        cdef np.ndarray[np.float64_t, ndim=1] replaceY = np.ndarray((self.index+1),dtype=np.float64)
        for i in range(self.index):
            replaceX[i] = self.xAxis[i]
            replaceY[i] = self.yAxis[i]
        self.xAxis = replaceX
        self.yAxis = replaceY
        self.yAxis[self.index] = y 
        if x != -1:
            self.xAxis[self.index] = x 
        else:
            self.xAxis[self.index] = self.index
        self.index += 1
        ret1,ret2 = (np.asarray(self.xAxis),np.asarray(self.yAxis))
        self.signal.emit(ret1,ret2)
        return (ret1,-2.5*np.log(ret2))

    cdef plotAxes(self, np.ndarray[np.float64_t, ndim=1] x, np.ndarray[np.float64_t, ndim=1] y):
        self.xAxis = x
        self.yAxis = y
        self.index = x.shape[0] - 1
        while (self.index > 0 and x[self.index] != 0):
            self.index -= 1
        if self.index == 0:
            self.index = x.shape[0] -1
        self.signal.emit(x,y)
        return (x,-2.5*np.log(y))

    cpdef draw(self, object args):
        if len(args) == 1:
            return self.append(args[0])
        else:
            x = args[0]
            y = args[1]
            if isinstance(y,float): ######Foreign to me, may be a bug source######
                return self.append(y,x)
            else:
                return self.plotAxes(x,y)

    def reset(self):
        self.xAxis = np.arange(0,1000,dtype=np.float64)
        self.yAxis = np.zeros_like(self.xAxis,dtype=np.float64)
        self.index = 0
#         self.plotAxes(self.xAxis,self.yAxis)