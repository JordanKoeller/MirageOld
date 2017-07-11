'''
Created on May 31, 2017

@author: jkoeller
'''


#Code associated with constructing/deconstructing an instance of a Parameters Class 
import math

from PyQt5 import QtCore

from Controllers import GUIController
from Controllers.FileManagers import ParametersFileManager
from Models.Stellar.Galaxy import Galaxy
from Models.Parameters.Parameters import Parameters
from Models.Stellar.Quasar import Quasar
from Models.ParametersError import ParametersError
from Models.Model import Model
import astropy.units as u
from astropy import constants as const
from Calculator import UnitConverter
from Views.GUI.HelpDialog import HelpDialog
from astropy.coordinates import SkyCoord
import random
from Utility import Vector2D

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
        GUIController.__init__(self, view,None,None)
        view.addSignals(paramLabel = self.paramLabel_signal, paramSetter = self.paramSetter_signal)
        self.view.load_setup.triggered.connect(self.loadParams)
        self.view.save_setup.triggered.connect(self.saveParams)
        self.view.scaleUnitOption.currentTextChanged.connect(self.updateUnitLabels)
        self.view.parametersEntryHelpAction.triggered.connect(self.displayHelpMessage)
        self.view.qVelRandomizer.clicked.connect(self.randomizeGVelocity)
        self.view.signals['paramSetter'].connect(self.bindFields)
        self.fileManager = ParametersFileManager(self.view.signals)
        self._tmpStars = []
    def displayHelpMessage(self):
        dialog = HelpDialog(self.view)
        dialog.show()
        
    def hide(self):
        self.view.mainSplitter.setSizes([0,100,100])
#         self.view.paramFrame.setHidden(True)
#         self.view.queueBox.setHidden(True)
#         self.view.visualizationBox.setHidden(True)
        
    def show(self):
        pass
        
    def buildParameters(self,extrasBuilder = None):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        Stores them in a Parameters object.
        If the user inputs invalid arguments, will handle the error by returning None and sending a message
        to the progress_label_slot saying "Error. Input could not be parsed to numbers."
        """
        # try:
        if True:
            gRedshift = float(self.view.gRedshift.text())
            qRedshift = float(self.view.qRedshift.text())
            qBHMass = u.Quantity(float(self.view.quasarBHMassEntry.text()),'solMass')
            specials = UnitConverter.generateSpecialUnits(qBHMass,qRedshift,gRedshift)
            with u.add_enabled_units(specials):
                #Setting units
                inputUnit = self.view.scaleUnitOption.currentText()
                print("Input unit = "+inputUnit)
                #Determination of relative motion
                gVelocity = self.view.vectorFromQString(self.view.qVelocity.text(),unit='km/s')


                gPositionRaDec = self.view.gPositionEntry.text()
                ra,dec = gPositionRaDec.strip('()').split(',')
                gPositionRaDec = SkyCoord(ra,dec, unit = (u.hourangle,u.deg))

                #Quasar properties
                qPosition = self.view.vectorFromQString(self.view.qPosition.text(), unit='arcsec').to('rad')
                qRadius = u.Quantity(float(self.view.qRadius.text()), 'uas')
                
                #Galaxy properties
                gVelDispersion = u.Quantity(float(self.view.gVelDispersion.text()), 'km/s')
                gNumStars = int(self.view.gNumStars.text())
                gShearMag = float(self.view.gShearMag.text())
                gShearAngle = u.Quantity(float(self.view.gShearAngle.text()), 'degree')
                gStarStdDev = float(self.view.gStarStdDev.text())
                gStarMean = gVelDispersion
                gStarParams = None
                if gNumStars == 0 or gStarStdDev == 0:
                    gStarParams = None
                else:
                    gStarParams = (gStarMean,gStarStdDev)
                displayCenter = self.view.vectorFromQString(self.view.gCenter.text(), unit='arcsec').to('rad')
                dTheta = u.Quantity(float(self.view.scaleInput.text()), inputUnit).to('rad').value
                print("dTheta = "+str(dTheta))
                canvasDim = int(self.view.dimensionInput.text())
                displayQuasar = self.view.displayQuasar.isChecked()
                displayGalaxy = self.view.displayGalaxy.isChecked()
    
                galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gNumStars, center=displayCenter, starVelocityParams=gStarParams,skyCoords = gPositionRaDec, velocity = gVelocity,stars = self._tmpStars)
                quasar = Quasar(qRedshift, qRadius, qPosition, gVelocity, mass = qBHMass)
                params = Parameters(galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
                self._tmpStars = []
                if self.view.qRadiusUnitOption.currentIndex() == 1:
                    absRg = (params.quasar.mass*const.G/const.c/const.c).to('m')
                    angle = absRg/params.quasar.angDiamDist.to('m')
                    params.quasar.update(radius = u.Quantity(angle.value*qRadius.value,'rad'))
                self.view.pixelAngleLabel_angle.setText(str(self.__round_to_n(params.pixelScale_angle.value,4)))
                self.view.pixelAngleLabel_thetaE.setText(str(self.__round_to_n(params.pixelScale_thetaE,4)))
                self.view.pixelAngleLabel_Rg.setText(str(self.__round_to_n(params.pixelScale_Rg,4)))
                self.view.quasarRadiusRGEntry.setText(str(self.__round_to_n(params.quasarRadius_rg, 4)))
                if extrasBuilder:
                    extrasBuilder(self.view,params,inputUnit)
                return params
        # except (AttributeError, ValueError) as e:
        #     self.view.signals['progressLabel'].emit("Error. Input could not be parsed to numbers.")
        #     return None
        # except ParametersError as e:
        #     self.view.signals['progressLabel'].emit(e.value)
        #     return None
        # except SyntaxError as e:
        #     self.view.signals['progressLabel'].emit("Syntax error found in trial variance code block.")
        #     return None
        
    def updateUnitLabels(self,unitString):
#         self.view.unitLabel_1.setText(unitString)
        self.view.unitLabel_3.setText(unitString)
        self.view.unitLabel_4.setText(unitString)
        self.view.unitLabel_6.setText(unitString)

    def randomizeGVelocity(self):
        x,y,z = ((random.random() - 0.5)*2,(random.random() - 0.5)*2,(random.random()-0.5)*2)
        res = (x*x+y*y+z*z)**(0.5)
        x /= res
        y /= res
        z /= res
        vel = np.array([x,y,z])
        vel = vel*(random.random()*1e9)
        self.view.qVelocity.setText('(' + str(int(vel[0])) + ","+ str(int(vel[1])) + "," + str(int(vel[2]))+")")

    def bindFields(self, parameters,bindExtras = None):
        """Sets the User interface's various input fields with the data in the passed-in parameters object."""
        if parameters.stars != []:
            self._tmpStars = parameters.galaxy.stars
        else:
            self._tmpStars = []
        with u.add_enabled_units(parameters.specialUnits):
            qV = parameters.quasar.velocity.to('rad').unitless()*parameters.quasar.angDiamDist.to('km').value;
            qP = parameters.quasar.position.to(self.view.qPositionLabel.text()).unitless()
            gP = parameters.galaxy.position.to('arcsec').unitless()
            self.view.qVelocity.setText("(" + str(qV.y) + "," + str(qV.x) + ")")
            self.view.qPosition.setText("(" + str(qP.y) + "," + str(qP.x) + ")")
            self.view.gCenter.setText("(" + str(gP.y) + "," + str(gP.x) + ")")
            self.view.qRadius.setText(str(parameters.quasar.radius.to(self.view.qRadiusUnitOption.currentText()).value))
            self.view.qRedshift.setText(str(parameters.quasar.redshift))
            self.view.gRedshift.setText(str(parameters.galaxy.redshift))
            self.view.gVelDispersion.setText(str(parameters.galaxy.velocityDispersion.value))
            self.view.gNumStars.setText(str(int(parameters.galaxy.percentStars*100)))
            self.view.gShearMag.setText(str(parameters.galaxy.shearMag))
            self.view.gShearAngle.setText(str(parameters.galaxy.shearAngle.to('degree').value))
            self.view.scaleInput.setText(str(parameters.dTheta.to(self.view.scaleUnitOption.currentText()).value * parameters.canvasDim))
            self.view.dimensionInput.setText(str(parameters.canvasDim))
            self.view.displayQuasar.setChecked(parameters.showQuasar)
            self.view.displayGalaxy.setChecked(parameters.showGalaxy)
            self.view.quasarBHMassEntry.setText(str(parameters.quasar.mass.to('solMass').value))
            if bindExtras:
                bindExtras(self.view,parameters)
        
    def __round_to_n(self, x,n = 6):
        if x == 0.0:
            return 0
        else:
            return round(float(x), -int(math.floor(math.log10(abs(float(x))))) + (n - 1))
            
    def saveParams(self):
        """Prompts the user for a file name, then saves the lensing system's parameters to be loaded in at a later session."""
        print("Firing")
        self.fileManager.write(Model.parameters or self.buildParameters())

    def loadParams(self):
        """Prompts the user to select a previously saved lensing system configuration, then when selected loads the system to model"""
        params = self.fileManager.read()
        if params:
            self.view.signals['paramSetter'].emit(params)
            
            
