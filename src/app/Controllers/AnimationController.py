'''
Created on Jul 25, 2017

@author: jkoeller
'''
import time

from .MasterController import MasterController
from ..Utility import asynchronous
# from ..Utility.AsyncSignal import AsyncSignal, Listener, PipeSignal
from ..Preferences import GlobalPreferences
from multiprocessing import Process
from PyQt5 import QtGui


class AnimationController(MasterController):

    '''
    extends MasterController.

    
    Controller that continually calls calculate on its children in a timer. Useful for rendering animations.

    Runs animation calculations in a separate process to keep the GUI Thread responsive and fast. Communication is facilitated via 
    python's Pipe and Queue classes in the multiprocessing package.

    Constructor has three arguments: startSignal, pauseSignal, and stopSignal. All three must be instances of QtCore.pyqtSignal().

    Emitting startSignal will start the animation.
    Emitting pauseSignal will pause the signal, allowing it to be resumed later with another startSignal emission.
    Emitting stopSignal will reset the controller to the state it was in before animating anything.


    
    '''
    
    def __init__(self,*signals):
        MasterController.__init__(self)
        Process.__init__(self)
        self._animating = False
        sig0 = signals[0]
        sig1 = signals[1]
        sig2 = signals[2]
        sig3 = signals[3]
        sig0.connect(self.run)
        sig1.connect(self.pause)
        sig2.connect(self.stop)
        self._signals = [sig0,sig1,sig2,sig3]
        self.run()
        
    @asynchronous
    def run(self):
        self._animating = True
        interval = 1/GlobalPreferences['max_frame_rate']
        while self._animating:
            try:
                begin = time.clock()
                MasterController.run(self,())
                deltaT = time.clock()-begin
                self._signals[3].emit()
                if deltaT < interval:
                    time.sleep(interval-deltaT)
            except StopIteration:
                self._animating = False
                break

    def readSignals(self):
        for signal in self._signals:
            signal.get()

    def checkPaused(self):
        sig = self._signals[0]
        if sig.get():
            print("Paused")
            return False
        else:
            return True

    def checkStopped(self):
        sig = self._signals[1]
        if sig.get():
            return False
        else:
            return True

    def pause(self):
        self._animating = False
            
    def stop(self):
        self._animating = False
    
    