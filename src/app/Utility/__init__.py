from .Vec2D import Vector2D, zeroVector
from threading import Thread
from multiprocessing import Process

def asynchronous(fn):       
        def ret(*args,**kwargs):         
            th = Thread(target=fn,args=args,kwargs=kwargs)
            th.daemon = True
            return th.start()                  
        return ret  