'''
Created on Jun 12, 2017

@author: jkoeller
'''
import math

from astropy import units as u

from Models import Parameters
from Models.Stellar import Quasar, Galaxy


class ParameterInputParser(object):
    '''
    classdocs
    '''
    
    inputUnit = None

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def parse(self,view, errorSignal):
        try:
            return self._parseHelper(view)
        except AttributeError:
            errorSignal.emit("Error. Input could not be parsed to numbers.")
            return None
    
    def __round_to_n(self, x,n = 6):
        if x == 0.0:
            return 0
        else:
            return round(float(x), -int(math.floor(math.log10(abs(float(x))))) + (n - 1))
        
    def _parseHelper(self,view):
        inputUnit = self._inputUnit
        qVelocity = view.vectorFromQString(view.qVelocity.text(),unit=inputUnit).to('rad')
        qPosition = view.vectorFromQString(view.qPosition.text(), unit=inputUnit).to('rad')
        qRedshift = float(view.qRedshift.text())
        qBHMass = u.Quantity(float(view.quasarBHMassEntry.text()),'solMass')
        qRadius = u.Quantity(float(view.qRadius.text()), 'arcsec')

        gRedshift = float(view.gRedshift.text())
        gVelDispersion = u.Quantity(float(view.gVelDispersion.text()), 'km/s')
        gNumStars = int(view.gNumStars.text())
        gShearMag = float(view.gShearMag.text())
        gShearAngle = u.Quantity(float(view.gShearAngle.text()), 'degree')
        gStarStdDev = float(view.gStarStdDev.text())
        gStarMean = gVelDispersion
        gStarParams = None
        if gNumStars == 0 and gStarStdDev == 0:
            gStarParams = None
        else:
            gStarParams = (gStarMean,gStarStdDev)
        displayCenter = view.vectorFromQString(view.gCenter.text(), unit=inputUnit).to('rad')
        dTheta = u.Quantity(float(view.scaleInput.text()), inputUnit).to('rad')
        canvasDim = int(view.dimensionInput.text())
        displayQuasar = view.displayQuasar.isChecked()
        displayGalaxy = view.displayGalaxy.isChecked()

        quasar = Quasar(qRedshift, qRadius, qPosition, qVelocity, mass = qBHMass)
        galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gNumStars, center=displayCenter, starVelocityParams=gStarParams)
        params = Parameters(galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
        
        view.pixelAngleLabel_angle.setText(str(self.__round_to_n(params.pixelScale_angle.value,4)))
        view.pixelAngleLabel_thetaE.setText(str(self.__round_to_n(params.pixelScale_thetaE,4)))
        view.pixelAngleLabel_Rg.setText(str(self.__round_to_n(params.pixelScale_Rg,4)))
        view.quasarRadiusRGEntry.setText(str(self.__round_to_n(params.quasarRadius_rg, 4)))
#             print(zeroVector)
#             print(params)
        return params