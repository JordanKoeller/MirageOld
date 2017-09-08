from .FileManager import FileWriter


class CurveFileExporter(FileWriter):
	"""
	extends FileWriter

	Specialized FileWriter designed to write lightCurve data to a file.

	Can accept lightCurve data from multiple signals, and will write them all in one
	numpy file once each data set has been connected.

	"""
	def __init__(self):
		'''
		Constructor. No arguments.
		'''
		super(CurveFileExporter, self).__init__()
		self._data = {}
		self._signals = []

	def addSignal(self,sig):
		'''
		Adds a signal to listen to for lightCurve data to be sent through.
		'''
		sig.connect(self.write)
		self._signals.append(sig)
		
	def write(self,data):
		'''
		Method called to accept lightCurve data from signals.
		Once all data has been received, this method will write 
		all the collected data sets to file.
		'''
		self._data.update(data)
		if len(self._data) == len(self._signals):
			self.close()

	def close(self):
		'''
		Writes all the collected data to file. Will prompt the user for a filename, write the data, and close it.
		'''
		import numpy as np
		np.savez(self.getFile(),**self._data)

	@property
	def fileextension(self):
		return ".npz"