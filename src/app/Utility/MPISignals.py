from mpi4py import MPI
from enum import Enum
import numpy as np
from .NullSignal import NullSignal
from threading import Thread
import time
# from PyQt5.QtCore import QObject


class ProcessRole(Enum):
    MAIN_PROCESS = 0
    CALCULATION_PROCESS = 1
    RECORD_PROCESS = 2


class SignalCode(Enum):
    """A few enumerations to make 
    sending messages over MPI more readable."""
    START   = 91
    PAUSE   = 92
    RESET   = 93
    STOP    = 94
    ACCEPT  = 95
    REJECT  = 96
    DEFAULT = 99

class MPIDummy(object):
    '''Stand-in class for an MPI Context.
    Useful to prevent MPI communication
    calls from throwing errors when executing
    without MPI.'''

    printOnAttempt = False

    def __init__(self):
        pass

    def report(self):
        if self.printOnAttempt:
            print("Tried to call on MPIDummy")

    def send(*args,**kwargs):
        self.report()
    def isend(*args,**kwargs):
        self.report()
    def Isend(*args,**kwargs):
        self.report()
    def ISend(*args,**kwargs):
        self.report()
    def recv(*args,**kwargs):
        self.report()
    def irecv(*args,**kwargs):
        self.report()
    def Irecv(*args,**kwargs):
        self.report()
    def IRecv(*args,**kwargs):
        self.report()


class MPIListener(object):
    '''
    Class tasked with listening for messages passed by between
    processes via MPI. Once a message is heard, it emits that 
    message's associated signal in the local context.

    To add a message to listen to, must call the listenFor(msg,sender, tag, signal)
    message, or else it will not hear it.
    '''

    def __init__(self):
        # QObject.__init__(self)
        self._listenerArgs = []
        self._listenerThread = Thread(target=self.listenLoop)
        # self._listenerThread.start()


    def listenFor(self,sender,tag=SignalCode.DEFAULT,msg=None,signal=NullSignal):
        if isinstance(tag,SignalCode):
            tag = tag.value
        if isinstance(sender,ProcessRole):
            sender = sender.value
        self._listenerArgs.append([sender,tag,msg,signal])

    def listenLoop(self):
        # time.sleep(1)
        while True:
            # print("FDSA")
            for sig in self._listenerArgs:
                data = comm.recv(source = sig[0], tag=sig[1])
                # hasData, data = receiver.test()
                # if hasData:
                print("Would emit the data" + str(data))
                    # sig[3].emit(data)
                # else:
                #     receiver.Cancel()
            # time.sleep(0.1) 


def usingMPI():
    try:        
        comm = MPI.COMM_WORLD
        sz = comm.Get_size()
        return sz > 0
    except:
        return False
    
# def configureToRecord(yesno,filename=None):
#     if yesno:

#     else:
#         comm.

def sendContiguousArray(arr,dest,tag = SignalCode.DEFAULT): #Will update to be buffer-based, if necessary at a later time.
    if isinstance(dest,ProcessRole):
        dest = dest.value
    if isinstance(tag,SignalCode):
        tag = tag.value
    comm.isend(arr, dest=dest,tag=tag)

def sendSignal(data,dest,tag = SignalCode.DEFAULT):
    if isinstance(dest,ProcessRole):
        dest = dest.value
    if isinstance(tag,SignalCode):
        tag = tag.value
    comm.isend(data,dest=dest,tag=tag)

def sendString(data,dest,tag=SignalCode.DEFAULT):
    sendSignal(data,dest,tag)



comm = None
processRole = None
if usingMPI():
    comm = MPI.COMM_WORLD
    processRole = ProcessRole(comm.Get_rank())
else:
    comm = MPIDummy()