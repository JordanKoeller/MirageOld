from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Parameters import Parameters
from Stellar import Galaxy
from Stellar import Quasar
from Utility import Vector2D, zeroVector
from astropy import units as u
import time


class QueueHandler(object):
	"""Handles creating queues of runs to perform."""
	def __init__(self, arg):
		super(QueueHandler, self).__init__()
		self.arg = arg
		