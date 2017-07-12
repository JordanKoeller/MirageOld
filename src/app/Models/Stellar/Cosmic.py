from astropy.cosmology import WMAP7 as cosmo
from ..ParametersError import ParametersError

class Cosmic(object):
	__redshift = 0.0
	
	def __init__(self):
		pass

	@property
	def angDiamDist(self):
		return cosmo.angular_diameter_distance(self.__redshift).to('lyr')

	@property
	def redshift(self):
		return self.__redshift

	def updateCosmic(self,**kwargs):
		for key,value in kwargs.items():
			try:
				getattr(self,"_Cosmic__"+key)
				if value != None:
					setattr(self,"_Cosmic__"+key,value)
			except AttributeError as e:
				raise ParametersError("failed to update "+key+ " in Cosmic")

	def cosmicString(self):
		return "redshift = " + str(self.redshift) + "\nAngDiamDist = " + str(self.angDiamDist)
