import math

from astropy import constants as const
from scipy.optimize import broyden1 as Solver

from ..Utility import Vector2D


class __ImageFinder(object):
	"""docstring for ImageFinder"""
	def __init__(self):
		pass
		# super(__ImageFinder, self).__init__()
		
	def _r_phi_x(self,parameters,beta,phi):
		Ksis = parameters.einsteinRadius #radians
		shear = parameters.shear
		K = shear.magnitude*math.sin(2*(math.pi/2 - shear.angle.value))
		c1 = 1 + shear.magnitude*math.sin(2*(math.pi/2 - shear.angle.value)) - shear.magnitude*math.cos(2*(math.pi/2 - shear.angle.value))
		r = (beta + Ksis*math.cos(phi))/(K+c1*math.cos(phi))

	def _r_phi_y(self,parameters,beta):
		Ksis = parameters.einsteinRadius #radians
		shear = parameters.shear
		K = shear.magnitude*math.sin(2*(math.pi/2 - shear.angle.value))
		c2 = 1 + shear.magnitude*math.sin(2*(math.pi/2 - shear.angle.value)) + shear.magnitude*math.cos(2*(math.pi/2 - shear.angle.value)) 
		r = (beta + Ksis*math.sin(phi))/(K+c2*math.sin(phi))



ImageFinder = __ImageFinder()