import pickle
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import imageio
import numpy as np

class IOThread(QtCore.QThread):
	"""docstring for IOThread"""
	def __init__(self,runMethod):
		super(IOThread, self).__init__()
		self.run = runMethod




class FileManager(object):
	"""docstring for FileManager"""
	filename = ''
	def __init__(self,singals):
		super(FileManager, self).__init__()
		self.recording = False
		self.__frames = []
		self.__frameCounter = 0
		self.progress_bar_update  = singals[0]
		self.progress_label_update = singals[1]
		self.progress_bar_max_update = singals[4]
		self.IOThread = IOThread(self.__runMethod)

	def __makeFile(self):
		return QtWidgets.QFileDialog.getSaveFileName()[0]

	def __getFile(self):
		return QtWidgets.QFileDialog.getOpenFileName()[0]

	def writeParams(self, parameters):
		self.filename = self.__makeFile()
		with open(self.filename,"wb+") as file:
			pickle.dump(parameters,file)
	def readParams(self):
		self.filename = self.__getFile()
		if self.filename:
			with open(self.filename,"rb") as file:
				return pickle.load(file)

	def __asNPArray(self,im):
		im = im.convertToFormat(4)
		width = im.width()
		height = im.height()
		ptr = im.bits()
		ptr.setsize(im.byteCount())
		arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
		return arr
	
	def giveFrame(self,frame):
		if self.recording:
			self.__frames.append(frame.copy())
			self.__frameCounter += 1


	def __runMethod(self):
		writer = imageio.get_writer(self.filename,fps=60)
		counter = 0
		for frame in self.__frames:
			img = self.__asNPArray(frame)
			writer.append_data(img)
			counter  += 1
			self.progress_bar_update.emit(counter)
		writer.close()
		self.progress_label_update.emit("File Saved.")
		self.__frames = []
		self.__frameCounter = 0
		self.progress_bar_update.emit(0)
		

	def save(self):
		if self.recording:
			self.filename = self.__makeFile()
			if self.filename:
				self.progress_bar_max_update.emit(self.__frameCounter)
				self.progress_label_update.emit("Rendering. Please Wait.")
				self.IOThread.start()
			self.recording = False


		