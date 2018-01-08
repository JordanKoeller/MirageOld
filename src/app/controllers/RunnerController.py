'''
Created on Dec 24, 2017

@author: jkoeller
'''
import math

from app.controllers.Controller import Controller
from PyQt5.QtWidgets import QApplication

import numpy as np

class Runner(Controller):
    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        Controller.__init__(self,*args,**kwargs)
        self._runningBool = False
        self._initialized = False
        self._spawnedGen = None
        
    def trigger(self,model,masterController):
        if self._runningBool:
            self.halt()
        else:
            if not self._initialized:
                self.initialize(model,masterController)
                self._spawnedGen = self.generator(model,masterController)
            self._runningBool = True
            while self._runningBool:
                try:
                    frame = next(self._spawnedGen)
                    self.broadcast(model, masterController, frame)
                except StopIteration:
                    self._runningBool = False
                    self._initialized = False
                
    def halt(self):
        print("Halting")
        self._runningBool = False
        
    def reset(self):
        self.halt()
        self._initialized = False
    
    def broadcast(self,model,masterController,frame):
        masterController.parametersController.update(model.parameters)
        masterController.lensedImageController.setLensedImg(model,frame)
        masterController.lightCurveController.add_point_and_plot(frame)
#         masterController.magMapController.update(model.parameters)
        model.parameters.incrementTime(model.parameters.dt)
        QApplication.processEvents()
        
    def initialize(self,model,masterController):
        print("Calling initialize")
        self._initialized = True
            
    def generator(self,model,masterController):
        pass
    
class AnimationRunner(Runner):
    '''
    Controller for generating animations, like videos.
    '''
    

    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        Runner.__init__(self,*args,**kwargs)
                        
    def generator(self, model, masterController):
        while True:
            yield model.engine.get_frame()
    
    def initialize(self, model, masterController):
        Runner.initialize(self, model, masterController)
                
    def halt(self):
        self._runningBool = False

    #NEED TO CHANGE THIS TO THE NEW INTERFACE

class FrameRunner(Runner):
    
    def __init__(self,*args,**kwargs):
        Runner.__init__(self,*args,**kwargs)
        
    def initialize(self, model, masterController):
        Runner.initialize(self, model, masterController)
    
    def generator(self,model, masterController):
        yield model.engine.getFrame()
        raise StopIteration
        
        
    # THIS ONE TOO
        
class LightCurveFollowerRunner(Runner):
    
    def __init__(self,*args,**kwargs):
        Runner.__init__(self,*args,**kwargs)
        self._counter = 0
        self._xStepArr = 0
        self._yStepArr = 0
        self._generator = None
        
    def initialize(self,model,masterController): 
        Runner.initialize(self, model, masterController) 
        lcparams = model.parameters.getExtras('lightcurve')
        begin = lcparams.pathStart.to('rad')
        end = lcparams.pathEnd.to('rad')
        resolution = lcparams.resolution
        dist = begin.distanceTo(end)
        xAxis = np.arange(0,dist,dist/resolution)
        masterController.lightCurveController.reset(xAxis)
        self._xStepArr = np.arange(begin.x,end.x,math.fabs(end.x-begin.x)/resolution)
        self._yStepArr = np.arange(begin.y,end.y,math.fabs(end.y-begin.y)/resolution)
        self._counter = 0
        
    def generator(self, model, masterController):
        while self._counter < len(self._xStepArr):
            x = self._xStepArr[self._counter]
            y = self._yStepArr[self._counter]
            yield model.engine.getFrame(x,y)
            self._counter += 1
        raise StopIteration
        
        
        
        
