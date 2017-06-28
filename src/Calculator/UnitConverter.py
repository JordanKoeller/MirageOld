from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo

def generateSpecialUnits(qMass,qR,gR):
    linearRg = (qMass.to('kg')*const.G/const.c/const.c).to('m')
    angleRg = linearRg/cosmo.angular_diameter_distance(qR)
    rgUnit = u.def_unit('r_g',(1/angleRg.value)*u.rad)
    thetaE = 4*const.G*u.Quantity(0.5,'solMass')*cosmo.angular_diameter_distance_z1z2(gR,qR)/const.c/const.c/cosmo.angular_diameter_distance(qR)/cosmo.angular_diameter_distance(gR)
    thetaEUnit = u.def_unit('theta_E',thetaE.value*u.rad)
    return [thetaEUnit,rgUnit]
