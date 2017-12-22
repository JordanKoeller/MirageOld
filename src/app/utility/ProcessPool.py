# '''
# Created on Aug 28, 2017
# 
# @author: jkoeller
# '''

import multiprocessing
import threading
import time

class ProcessHandler(object):
    
    def __init__(self):
        self._process = multiprocessing.Process()
        self._inbox = multiprocessing.Queue()
        self._active = True
        self._listener = threading.Thread(run=self._listen)
        
    def sendMessage(self,msg):
        self._inbox.send(msg)
        
    def sendFunction(self,fn,args=None,kwargs=None):
        self._inbox.send(fn,args=args,kwargs=kwargs)
        
    @property
    def processID(self):
        return self._process.process_id()
    
    def _listen(self):
        while self._active:
            if not self._inbox.empty():
                msg = self._inbox.get()
                print(msg) #Temporary. Will update with real method invocation later
            time.sleep(0.1)

        
    
    