from __future__ import division
import numpy as np 
from PyQt5 import QtGui, QtCore


class CanvasDrawer(object):
	"""Controls drawing of images:
	------ Options --------
	If showing an image:
	    define canvas size - will need to be 2d again
	    show galaxy
	    show quasar
	    show stars
	    show einstein radius
	If showing a light curve:
	    show light curve at top
	    define canvas size - will need to be 2d
	    show axes?
	    trace curve as a function of time
	        Need to refactor how I update the position of the quasar



	"""
	def __init__(self, arg):
		super(CanvasDrawer, self).__init__()


	def draw(dataArray = None, magnification = False): #Mutates array, rather than returning a copy? OR return an instance of QImage/QPixmap
		pass
		