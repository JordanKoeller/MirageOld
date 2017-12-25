'''
Created on Dec 24, 2017

@author: jkoeller
'''
from app.controllers.Controller import Controller
# from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

class Runner(Controller):
    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        Controller.__init__(self,*args,**kwargs)
        self._runningBool = False
        
    def trigger(self,model,masterController):
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
        
    def trigger(self,model,masterController):
        model.bind_parameters()
        if self._runningBool:
            self._runningBool = False
        else:
            self._runningBool = True
            while self._runningBool:
                frame = model.engine.getFrame()
                print(type(frame))
#                 masterController.parametersController.update(model.parameters)
                masterController.lensedImageController.setLensedImg(model,frame)
                masterController.lightCurveController.update(frame)
#                 masterController.magMapController.update(model.parameters)
                model.parameters.incrementTime(model.parameters.dt)
                QApplication.processEvents()


class FrameRunner(Runner):
    
    def __init__(self,*args,**kwargs):
        Runner.__init__(self,*args,**kwargs)
        
    def trigger(self,model,masterController):
        frame = model.engine.getFrame()
        masterController.lensedImageController.update(frame)
        masterController.lightCurveController.update(frame)
        masterController.parametersController.update(model.parameters)
        masterController.magMapController.update(model.parameters)        
        
