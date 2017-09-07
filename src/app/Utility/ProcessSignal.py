'''
Created on Aug 28, 2017

@author: jkoeller
'''
from multiprocessing import Pipe 


class PipeSignal(object):
    '''
    classdocs
    '''


    def __init__(self, signal,listener=None):
        '''
        Constructor
        '''
        self._signal = signal
        self._send, self._rcv = Pipe()
        self._listener = listener
        
    def connect(self,slot):
        self._slot = slot
        self._signal.connect(self._slot)
        
    def emit(self,*args):
        self._send.send(args)
        
    def _listen(self):
        if self._rcv.poll():
            try:
                emitter = self._recv.recv()
                self._signal.emit(*emitter)
            except EOFError:
                pass
            
            
