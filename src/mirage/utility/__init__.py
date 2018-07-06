import concurrent.futures
from multiprocessing import Process, Queue
from threading import Thread

# from .AsyncSignal import AsyncSignal, Listener
from .Vec2D import Vector2D, zeroVector, Vector2DJSONDecoder
from .SignalRepo import SignalObject, SignalRepo
from .QuantityJSONEncoder import QuantityJSONDecoder, QuantityJSONEncoder
from .ParametersError import ParametersError
from .NullSignal import NullSignal

def asynchronous(fn):       
        def ret(*args,**kwargs):         
            th = Thread(target=fn,args=args,kwargs=kwargs)
            th.daemon = True
            return th.start()                  
        return ret


# def asynchronous(fn):       
#         def ret(*args,**kwargs):         
#             with concurrent.futures.ProcessPoolExecutor() as executor:
#             	executor.submit(fn,args,kwargs)
#         return ret


_listener = None

# def asynchronous(inSignals=None,outsignals=None):
# 	global _listener
# 	if not _listener:
# 		_listener = Listener()
# 		_listener.start()
# 	def decorator(fn):
# 		wrappedSignal = AsyncSignal(fn,_listener)
# 		def decorated(self,*args,**kwargs):
# 			th = Process(target=fn,args=args,kwargs=kwargs)
# 			th.daemon = True
# 			wrappedSignal.emit(th.start())
# 		return decorated
# 	return decorator