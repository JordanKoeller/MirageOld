from multiprocessing import Pipe
from threading import Thread 

from PyQt5.QtCore import QObject


class Listener(Thread,QObject):

	def __init__(self,parent=None):
		Thread.__init__(self)
		# QTimer.__init__(self,parent)
		QObject.__init__(self)
		self.connections = []
		self.daemon = True

	def addConnection(self,signal):
		recv, send = Pipe()
		self.connections.append((recv,signal))
		return send


	def run(self):
		while True:
			for connection,signal in self.connections:
				try:
					objs = connection.recv()
				except EOFError:
					break
				else:
					signal.emit(*objs)


_listener = None#_Listener()
# _listener.start(0)



class AsyncSignal(object):
	'''Decorator class for a pyqt signal, allowing the signal to be sent
	between processes. Should instantiate by calling Utility.RemoteConnection, not 
	directly.'''

	def __init__(self,signal,listener = None):
		self.signal = signal
		if not listener:
			global _listener
			if not _listener:
				_listener = Listener()
				_listener.start()
			# if _listener:
			self._emitter = _listener.addConnection(self.signal)
		else:
			self._emitter = listener.addConnection(self.signal)
	def emit(self, *args):
		# print(args)
		self._emitter.send(args)

	def connect(self,fn):
		self.signal.connect(fn)


class PipeSignal(object):

	def __init__(self,signal):
		self.recv,self.send = Pipe()
		self.signal = signal
		self.signal.connect(self.emit)

	def connect(self,fn):
		self.fn = fn

	def get(self):
		if self.recv.poll():
			try:
				emitter = self.recv.recv()
			except EOFError:
				return False
			else:
				return True

	def emit(self,*args):
		self.send.send(args)
