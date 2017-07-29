from ...Models.Model import Model
from ...Utility.NullSignal import NullSignal
from ...Views.Drawer.LensedImageDrawer import LensedImageDrawer
from ..Controller import Controller
from ...Views.Drawer.Drawer import PlotDrawer

import numpy as np


# MODELQUESTIONERDELEGATES
class ParametersGetter(Controller):
    
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self,*args,**kwargs):
        return Model.parameters

class TrajectoryParametersGetter(Controller):
    def __init__(self):
        Controller.__init__(self)

    def calculate(self,*args,**kwargs):
        Model.parameters.incrementTime(Model.parameters.dt)
        return Model.parameters
    

#DATAFETCHERDELEGATE

class PixelFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self, *args, **kwargs):
        return Model.engine.getFrame()
    
class MagnificationFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self):
            return Model.engine.getMagnification(None)
    
class LightCurveFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self, min,max,resolution):
        return Model.engine.makeLightCurve(min,max,resolution)
    
class MagMapFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self, center,dims,resolution,signal=NullSignal,signalMax = NullSignal):
        return Model.engine.makeMagMap(center,dims,resolution,signal,signalMax) 


        
#POSTPROCESSING

class FrameDrawerDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        self._drawer = LensedImageDrawer()
        
    def calculate(self,pixels):
        parameters = Model.parameters
        return self._drawer.draw((parameters,pixels))
        
class CurveDrawerDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        self._drawer = PlotDrawer()
    def calculate(self,data):
        if isinstance(data,int):
            return self._drawer.append(data)
        else:
            return self._drawer.append(Model.engine.getMagnification(len(data)))



#EXPORTERS
        
class CurveExporter(Controller):
    def __init__(self,signal):
        Controller.__init__(self)
        self._signal = signal
    
    def calculate(self, data):
        self._signal.emit(data)
        
class FrameExporter(Controller):
    def __init__(self,signal):
        Controller.__init__(self)
        self._signal = signal
        
    def calculate(self, frame):
        self._signal.emit(frame)
        