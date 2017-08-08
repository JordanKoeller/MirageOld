from app.Models import Model
from ...Utility.NullSignal import NullSignal
from ...Views.Drawer.LensedImageDrawer import LensedImageDrawer
from ..Controller import Controller
from ...Views.Drawer.Drawer import PlotDrawer
from ...Utility.Vec2D import Vector2D
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
    
class MagMapModelGetter(Controller):
    def __init__(self,mname,startTrace,endTrace):
        Controller.__init__(self)
        self.modelID = mname
        startTrace = Vector2D(startTrace[0],startTrace[1])
        endTrace = Vector2D(endTrace[0],endTrace[1])
        Model[self.modelID].modelID = self.modelID
        self.track = Model[self.modelID].engine.makePixelSteps(startTrace,endTrace)
        self.trackGenerator = self.getNextPos()

    def getNextPos(self):
        for x,y in self.track:
            yield Model[self.modelID].magMapParameters.pixelToAngle(Vector2D(x,y))

    def calculate(self,*args):
        Model[self.modelID].parameters.quasar.setPos(next(self.trackGenerator))
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
        if isinstance(data,np.ndarray):
            return (model,self._drawer.append(model.engine.getMagnification(len(data))))
        else:
            return (model,self._drawer.append(data))

class NullDelegate(Controller):
    def __init__(self,*args,**kwargs):
        Controller.__init__(self)

    def calculate(self,*args):
        return args

class MagMapTracerDelegate(Controller):
    def __init__(self):
        Controller.__init__(self)

    def calculate(self,model,data,*args):
        pos = model.parameters.quasar.observedPosition
        pixPos = model.magMapParameters.angleToPixel(pos)
        return (model,pixPos.asTuple)



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
        
class MagMapTracerExporter(Controller):
    def __init__(self,signal):
        Controller.__init__(self)
        self._signal = signal

    def calculate(self,model,data):
        self._signal.emit((model,data))