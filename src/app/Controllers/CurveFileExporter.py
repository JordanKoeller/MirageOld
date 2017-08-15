from .FileManager import FileWriter

class CurveFileExporter(FileWriter):
	"""Accepts light curve data via the passed-in signal. Has two parameters:

	signals: channels by which controllers send their data.
	destination: (optional) filename to save to. If none supplied, will open a dialog and make its own."""
	def __init__(self):
		super(CurveFileExporter, self).__init__()
		self._data = {}
		self._signals = []

	def addSignal(self,sig):
		sig.connect(self.write)
		self._signals.append(sig)
		
	def write(self,data):
		self._data.update(data)
		if len(self._data) == len(self._signals):
			self.close()

	def close(self):
		import numpy as np
		np.savez(self.getFile(),**self._data)

	@property
	def fileextension(self):
		return ".npz"