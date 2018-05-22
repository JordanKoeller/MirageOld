import math

from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo


# def generateSpecialUnits(qMass,qR,gR):
#     rgUnit = u.def_unit('r_g',(1/angleRg.value)*u.rad)
#     thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
#     return [thetaEUnit,rgUnit]
def _scaleFactor(qR,gR):
	return (cosmo.angular_diameter_distance_z1z2(gR,qR)/cosmo.angular_diameter_distance(qR)/cosmo.angular_diameter_distance(gR)).to('1/m')

# @property
# def avgMassEinsteinRadius(self):
# 	avgMass = self.galaxy.averageStarMass
# 	gR = self.galaxy.redshift
# 	qR = self.quasar.redshift
# 	thetaE = 4*const.G*u.Quantity(avgMass,'solMass').to('kg')*self.dLS.to('m')/self.quasar.angDiamDist.to('m')/self.galaxy.angDiamDist.to('m')/const.c/const.c
# 	thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
# 	return thetaEUnit

def generateSpecialUnits(qMass,qR,gR):
	linearRg = (qMass.to('kg')*const.G/const.c/const.c).to('m')
	angleRg = linearRg/cosmo.angular_diameter_distance(qR)
	rgUnit = u.def_unit('r_g',angleRg.value*u.rad)
	thetaE = 4*const.G*u.Quantity(0.5,'solMass').to('kg')*_scaleFactor(qR,gR)/const.c/const.c
	thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
	return [thetaEUnit,rgUnit]
	