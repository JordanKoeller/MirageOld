'''
Created on May 31, 2017

@author: jkoeller
'''


#Code associated with constructing/deconstructing an instance of a Parameters Class 
from Controllers.GUIController import GUIController
from Models import Galaxy
from Models import Parameters
from Models import Quasar
from Utility import Vector2D
import astropy.units as u


class ParametersController(GUIController):
    '''
    For Controlling user input to specify the parameters for the run
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
        
    def makeParameters(self,view):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        Stores them in a Parameters object.
        If the user inputs invalid arguments, will handle the error by returning None and sending a message
        to the progress_label_slot saying "Error. Input could not be parsed to numbers."
        """
        try:
            qVelocity = self.__vector_from_qstring(view.qVelocity.text()).setUnit('arcsec').to('rad')
            qPosition = self.__vector_from_qstring(view.qPosition.text()).setUnit('arcsec').to('rad')
            qRadius = u.Quantity(float(view.qRadius.text()), 'arcsec')
            qRedshift = float(view.qRedshift.text())

            gRedshift = float(view.gRedshift.text())
            gVelDispersion = u.Quantity(float(view.gVelDispersion.text()), 'km/s')
            gNumStars = int(view.gNumStars.text())
            gShearMag = float(view.gShearMag.text())
            gShearAngle = u.Quantity(float(view.gShearAngle.text()), 'degree')

            displayCenter = self.__vector_from_qstring(view.gCenter.text()).setUnit('arcsec').to('rad')
            dTheta = u.Quantity(float(view.scaleInput.text()), 'arcsec').to('rad')
            canvasDim = int(view.dimensionInput.text())
            displayQuasar = view.displayQuasar.isChecked()
            displayGalaxy = view.displayGalaxy.isChecked()

            quasar = Quasar(qRedshift, qRadius, qPosition, qVelocity)
            galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gNumStars, center=displayCenter)
            params = Parameters(galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
            # params.circularPath = self.circularPathBox.isChecked()
            return params
        except ValueError:
            self.progress_label_slot("Error. Input could not be parsed to numbers.")
            return None


    def bindFields(self, parameters,view):
        """Sets the User interface's various input fields with the data in the passed-in parameters object."""
        qV = parameters.quasar.velocity.to('arcsec').unitless()
        qP = parameters.quasar.position.to('arcsec').unitless()
        gP = parameters.galaxy.position.to('arcsec').unitless()
        view.qVelocity.setText("(" + str(qV.y) + "," + str(qV.x) + ")")
        view.qPosition.setText("(" + str(qP.y) + "," + str(qP.x) + ")")
        view.gCenter.setText("(" + str(gP.y) + "," + str(gP.x) + ")")
        view.qRadius.setText(str(parameters.quasar.radius.to('arcsec').value))
        view.qRedshift.setText(str(parameters.quasar.redshift))
        view.gRedshift.setText(str(parameters.galaxy.redshift))
        view.gVelDispersion.setText(str(parameters.galaxy.velocityDispersion.value))
        view.gNumStars.setText(str(parameters.galaxy.numStars))
        view.gShearMag.setText(str(parameters.galaxy.shearMag))
        view.gShearAngle.setText(str(parameters.galaxy.shearAngle.to('degree').value))
        view.scaleInput.setText(str(parameters.dTheta.to('arcsec').value * parameters.canvasDim))
        view.dimensionInput.setText(str(parameters.canvasDim))
        view.displayQuasar.setChecked(parameters.showQuasar)
        view.displayGalaxy.setChecked(parameters.showGalaxy)
        
    def __vector_from_qstring(self, string, reverse_y=False, transpose=True):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

        Parameters:
            reverse_y : Boolean
                specify whether or not to negate y-coordinates to convert a conventional coordinate system of positive y in the up direction to
                positive y in the down direction as used by graphics libraries. Default False

            transpose : Boolean
                Specify whether or not to flip x and y coordinates. In other words, return a Vector2D of (y,x) rather than (x,y). Default True
        """
        x, y = (string.strip('()')).split(',')

        if transpose:
            if reverse_y:
                return Vector2D(-float(y), float(x))
            else:
                return Vector2D(float(y), float(x))
        else:
            if reverse_y:
                return Vector2D(float(x), -float(y))
            else:
                return Vector2D(float(x), float(y))
            
            
