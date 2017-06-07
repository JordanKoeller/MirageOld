'''
Created on May 31, 2017

@author: jkoeller
'''


#Code associated with constructing/deconstructing an instance of a Parameters Class 
import math

from PyQt5 import QtCore

from Controllers import GUIController
from Controllers.FileManagers import ParametersFileManager
from Models import Galaxy
from Models import Parameters
from Models import Quasar
import astropy.units as u


class ParametersController(GUIController):
    '''
    For Controlling user input to specify the parameters for the run
    '''

    paramLabel_signal = QtCore.pyqtSignal(str)
    paramSetter_signal = QtCore.pyqtSignal(object)

    def __init__(self,view):
        '''
        Constructor
        '''
        GUIController.__init__(self, view)
        view.addSignals(paramLabel = self.paramLabel_signal, paramSetter = self.paramSetter_signal)
        self.view.load_setup.triggered.connect(self.loadParams)
        self.view.save_setup.triggered.connect(self.saveParams)
        self.view.signals['paramSetter'].connect(self.bindFields)
        self.fileManager = ParametersFileManager(self.view.signals)
        
        
        
    def makeParameters(self):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        Stores them in a Parameters object.
        If the user inputs invalid arguments, will handle the error by returning None and sending a message
        to the progress_label_slot saying "Error. Input could not be parsed to numbers."
        """
        try:
            qVelocity = self.view.vectorFromQString(self.view.qVelocity.text(),unit='arcsec')
            qPosition = self.view.vectorFromQString(self.view.qPosition.text(), unit='arcsec')
            qRadius = u.Quantity(float(self.view.qRadius.text()), 'arcsec')
            qRedshift = float(self.view.qRedshift.text())
            qBHMass = u.Quantity(float(self.view.quasarBHMassEntry.text()),'solMass')

            gRedshift = float(self.view.gRedshift.text())
            gVelDispersion = u.Quantity(float(self.view.gVelDispersion.text()), 'km/s')
            gNumStars = int(self.view.gNumStars.text())
            gShearMag = float(self.view.gShearMag.text())
            gShearAngle = u.Quantity(float(self.view.gShearAngle.text()), 'degree')

            displayCenter = self.view.vectorFromQString(self.view.gCenter.text(), unit='arcsec')
            dTheta = u.Quantity(float(self.view.scaleInput.text()), 'arcsec').to('rad')
            canvasDim = int(self.view.dimensionInput.text())
            displayQuasar = self.view.displayQuasar.isChecked()
            displayGalaxy = self.view.displayGalaxy.isChecked()

            quasar = Quasar(qRedshift, qRadius, qPosition, qVelocity, mass = qBHMass)
            print(quasar)
            galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gNumStars, center=displayCenter)
            params = Parameters(galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
            self.view.pixelAngleLabel_angle.setText(str(self.__round_to_n(params.pixelScale_angle.value,4)))
            self.view.pixelAngleLabel_thetaE.setText(str(self.__round_to_n(params.pixelScale_thetaE,4)))
            self.view.pixelAngleLabel_Rg.setText(str(self.__round_to_n(params.pixelScale_Rg,4)))
            self.view.quasarRadiusRGEntry.setText(str(self.__round_to_n(params.quasarRadius_rg, 4)))
            return params
        except ValueError:
            self.view.signals['progressLabel'].emit("Error. Input could not be parsed to numbers.")
            return None


    def bindFields(self, parameters):
        """Sets the User interface's various input fields with the data in the passed-in parameters object."""
        qV = parameters.quasar.velocity.to('arcsec').unitless()
        qP = parameters.quasar.position.to('arcsec').unitless()
        gP = parameters.galaxy.position.to('arcsec').unitless()
        self.view.qVelocity.setText("(" + str(qV.y) + "," + str(qV.x) + ")")
        self.view.qPosition.setText("(" + str(qP.y) + "," + str(qP.x) + ")")
        self.view.gCenter.setText("(" + str(gP.y) + "," + str(gP.x) + ")")
        self.view.qRadius.setText(str(parameters.quasar.radius.to('arcsec').value))
        self.view.qRedshift.setText(str(parameters.quasar.redshift))
        self.view.gRedshift.setText(str(parameters.galaxy.redshift))
        self.view.gVelDispersion.setText(str(parameters.galaxy.velocityDispersion.value))
        self.view.gNumStars.setText(str(parameters.galaxy.numStars))
        self.view.gShearMag.setText(str(parameters.galaxy.shearMag))
        self.view.gShearAngle.setText(str(parameters.galaxy.shearAngle.to('degree').value))
        self.view.scaleInput.setText(str(parameters.dTheta.to('arcsec').value * parameters.canvasDim))
        self.view.dimensionInput.setText(str(parameters.canvasDim))
        self.view.displayQuasar.setChecked(parameters.showQuasar)
        self.view.displayGalaxy.setChecked(parameters.showGalaxy)
        self.view.quasarBHMassEntry.setText(str(parameters.quasar.mass.to('solMass').value))
        
    def __round_to_n(self, x,n = 6):
        if x == 0.0:
            return 0
        else:
            return round(float(x), -int(math.floor(math.log10(abs(float(x))))) + (n - 1))
            
    def saveParams(self):
        """Prompts the user for a file name, then saves the lensing system's parameters to be loaded in at a later session."""
        print("Firing")
        self.fileManager.write(self.makeParameters())

    def loadParams(self):
        """Prompts the user to select a previously saved lensing system configuration, then when selected loads the system to model"""
        params = self.fileManager.read()
        if params:
            self.view.signals['paramSetter'].emit(params)
            
            
