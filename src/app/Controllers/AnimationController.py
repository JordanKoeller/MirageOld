'''
Created on Jul 25, 2017

@author: jkoeller
'''
import time

from .MasterController import MasterController
from ..Utility import asynchronous
from ..Preferences import GlobalPreferences


class AnimationController(MasterController):
    
    def __init__(self,*args,**kwargs):
        MasterController.__init__(self,*args,**kwargs)
        self._animating = False
        
        
    @asynchronous
    def run(self):
        self._animating = True
        interval = 1/GlobalPreferences['max_frame_rate']
        while self._animating:
            begin = time.clock()
            MasterController.run(self)
            deltaT = time.clock()-begin
            if deltaT < interval:
                time.sleep(interval-deltaT)

    def pause(self):
        self._animating = False
            
    def stop(self):
        self._animating = False
    
    