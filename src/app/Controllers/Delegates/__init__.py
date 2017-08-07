from app.Models import Model
from ...Utility.NullSignal import NullSignal
from ...Views.Drawer.LensedImageDrawer import LensedImageDrawer
from ..Controller import Controller
from ...Views.Drawer.Drawer import PlotDrawer
# from ...Utility.AsyncSignal import AsyncSignal
import numpy as np


# MODELQUESTIONERDELEGATES
class ModelGetter(Controller):
    
    def __init__(self,mname):
        Controller.__init__(self)
        self.modelID = mname
        
    def calculate(self,*args):
        return (Model[self.modelID],)


class TrajectoryModelGetter(Controller):
    def __init__(self,mnane):
        Controller.__init__(self)
        self.modelID = mnane
        Model[self.modelID].modelID = self.modelID

    def calculate(self,*args):
        Model[self.modelID].parameters.incrementTime(Model[self.modelID].parameters.dt)
        return (Model[self.modelID],)
    


#DATAFETCHERDELEGATE

class PixelFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self,model,*args):
        return (model,model.engine.getFrame())
    
class MagnificationFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self,model,*args):
            return (model,model.engine.getMagnification(None))
    
class LightCurveFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self,model, min,max,resolution,*args):
        return (model,model.engine.makeLightCurve(min,max,resolution))
    
class MagMapFetcherDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        
    def calculate(self,model, center,dims,resolution,signal=NullSignal,signalMax = NullSignal,*args):
        return (model,ModelImpl.engine.makeMagMap(center,dims,resolution,signal,signalMax))


        
#POSTPROCESSING

class FrameDrawerDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        self._drawer = LensedImageDrawer()
        
    def calculate(self,model,pixels,*args):
        return (model,self._drawer.draw((model,pixels)))
        
class CurveDrawerDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)
        self._drawer = PlotDrawer()

    def calculate(self,model,data,*args):
        if isinstance(data,int):
            return (model,self._drawer.append(data))
        else:
            return (model,self._drawer.append(model.engine.getMagnification(len(data))))



#EXPORTERS
        
class CurveExporter(Controller):
    def __init__(self,signal):
        Controller.__init__(self)
        # self._signal = AsyncSignal(signal)
        self._signal = signal
    
    def calculate(self, model,data):
        self._signal.emit(data)
        
class FrameExporter(Controller):
    def __init__(self,signal):
        Controller.__init__(self)
        self._signal = signal
        # self._signal = AsyncSignal(signal)
        
    def calculate(self, model,data):
        self._signal.emit(data)
        