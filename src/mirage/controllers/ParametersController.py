'''
Created on Dec 22, 2017

@author: jkoeller
'''
import math
import random

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel
from astropy import constants as const
from astropy import units as u
import numpy as np

from mirage.calculator import UnitConverter
from mirage.parameters import Parameters
from mirage.parameters.stellar import Galaxy, Quasar
from mirage.utility import Vector2D, NullSignal
from . import Controller

class ParametersController(Controller):

    _emit_parameters = pyqtSignal(object)
    _force_model_update = pyqtSignal()


    def __init__(self):
        Controller.__init__(self)
        self.addSignals(view_update_signal = NullSignal,
            set_input_units = NullSignal,
            emit_parameters = self._emit_parameters,
            force_model_update = self._force_model_update)

    def set_view(self,view):
        self._view = view
        self._view.regenerateStars.pressed.connect(self._request_new_stars)
        self._qplabel = QLabel()
        self._view.statusBar.addWidget(self._qplabel)
        # self._qplabel = self._view.statusBar.children()[1]

    def update(self,p):
        self._view.signals['clear_message'].emit()
        qp = p.quasar.observedPosition.to('arcsec')
        x = qp.x
        y = qp.y
        x = "%.3f" % x
        y = "%.3f" % y
        s = "(" + x + "," + y + ")" + " arcsec"
        self._qplabel.setText(s)
        rg = p.quasar.radius.to(p.gravitationalRadius)
        te = p.quasar.radius.to(p.avgMassEinsteinRadius)
        self._view.quasarRadiusRGEntry.setText("%.3f" % rg.value)
        self._view.qRadiusThetaEEntry.setText("%.3f" % te.value)
        rgWidth = p.canvasDim*p.dTheta.to(p.gravitationalRadius)
        teWidth = p.canvasDim*p.dTheta.to(p.avgMassEinsteinRadius)
        self._view.pixelAngleLabel_thetaE.setText("%.3f" % teWidth.value)
        self._view.pixelAngleLabel_Rg.setText("%.3f" % rgWidth.value)

    def vectorFromQString(self, string, unit=None):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

        """
        x, y = (string.strip('()')).split(',')
        if ' ' in y:
            y = y.split(' ')[0]
        return Vector2D(float(x), float(y), unit)

    def bind_view_signals(self,viewSignals):
        pass

    def _request_new_stars(self):
        # self.signals['force_model_update'].emit()
        p = self.getParameters()
        self._model.set_parameters(p)
        self._model.regenerate_stars()
        numStars = self._model.parameters.galaxy.numStars
        self._view.numStarsLabel.setText("Generated " + str(numStars) + str(" stars"))
        self._model.bind_parameters()



    # @property
    def getParameters(self):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        returns them in a Parameters object.
        If the user inputs invalid arguments, will handle the error by returning None and sending a message
        to the progress_label_slot saying "Error. Input could not be parsed to numbers."
        """
        if self._isReadOnly:
            return None
        else:
            try:
                gRedshift = float(self._view.gRedshift.text())
                qRedshift = float(self._view.qRedshift.text())
                qBHMass = u.Quantity(float(self._view.quasarBHMassEntry.text()), 'solMass')
                specials = UnitConverter.generateSpecialUnits(qBHMass, qRedshift, gRedshift)
                with u.add_enabled_units(specials):
                    units = self.get_units()
                    apparentV = self.vectorFromQString(self._view.qVelocity.text(),units['qVel'])
                    qPosition = self.vectorFromQString(self._view.qPosition.text(),units['qPos']).to('rad')
                    qRadius = u.Quantity(float(self._view.qRadius.text()),units['qRadius']).to('uas')
                    gVelDispersion = u.Quantity(float(self._view.gVelDispersion.text()), 'km/s')
                    gNumStars = float(self._view.gNumStars.text())
                    gShearMag = float(self._view.gShearMag.text())
                    gShearAngle = u.Quantity(float(self._view.gShearAngle.text()), 'degree')
                    displayCenter = self.vectorFromQString(self._view.gCenter.text(),units['center']).to('rad')
                    dTheta = u.Quantity(float(self._view.scaleInput.text()), units['scale']).to('rad').value
                    canvasDim = int(self._view.dimensionInput.text())
                    galaxy = Galaxy(redshift=gRedshift,
                                    velocityDispersion=gVelDispersion,
                                    shearMag=gShearMag, shearAngle=gShearAngle,
                                    center=displayCenter,
                                    percentStars=gNumStars)
                    quasar = Quasar(redshift=qRedshift,
                                    radius=qRadius,
                                    position=qPosition,
                                    mass=qBHMass,
                                    velocity=apparentV)
                    params = Parameters(galaxy=galaxy,
                                        quasar=quasar,
                                        dTheta=dTheta,
                                        canvasDim=canvasDim)
                    # if self._view.qRadiusUnitOption.currentIndex() == 1:
                    #     absRg = (params.quasar.mass * const.G / const.c / const.c).to('m')
                    #     angle = absRg / params.quasar.angDiamDist.to('m')
                    #     params.quasar.update(radius=u.Quantity(angle.value * qRadius.value, 'rad'))
                    return params
            except:
                print("Failed building in ParametersController")
                return False

    def save(self):
        from mirage.io import ParametersFileManager
        data = self.getParameters()
        if data:
            filemanager = ParametersFileManager()
            filemanager.open()
            if filemanager.write(data):
                fname = filemanager._filename
                filemanager.close()
                self._view.signals['message'].emit(fname + " saved successfully.")
    
    def load(self):
        from mirage.io import ParametersFileReader
        filemanager = ParametersFileReader()
        if filemanager.open():
            params = filemanager.load()
            fname = filemanager._filename
            filemanager.close()
            if params:
                self._view.signals['message'].emit("Loaded data from " + fname + ".")
                self._bindFieldsHelper(params)

    def set_read_only(self, state):
        self._view.qVelocity.setReadOnly(state)
        self._view.qPosition.setReadOnly(state)
        self._view.gCenter.setReadOnly(state)
        self._view.qRadius.setReadOnly(state)
        self._view.qRedshift.setReadOnly(state)
        self._view.gRedshift.setReadOnly(state)
        self._view.gVelDispersion.setReadOnly(state)
        self._view.gNumStars.setReadOnly(state)
        self._view.gShearMag.setReadOnly(state)
        self._view.gShearAngle.setReadOnly(state)
        self._view.scaleInput.setReadOnly(state)
        self._view.dimensionInput.setReadOnly(state)
        self._view.quasarBHMassEntry.setReadOnly(state)
        self._view.regenerateStars.setDisabled(state)
        self._isReadOnly = state

    def bind_fields(self,parameters):
        return self._bindFieldsHelper(parameters)

    def _bindFieldsHelper(self, parameters):
        """Sets the User interface's various input fields with the data in the passed-in parameters object."""
        with u.add_enabled_units(parameters.specialUnits):
            unitmap = self.get_units()
            qP = parameters.quasar.position.to(unitmap['qPos']).unitless()
            gP = parameters.galaxy.position.to(unitmap['center']).unitless()
            self._view.qPosition.setText(qP.asString)
            self._view.gCenter.setText(gP.asString)
            self._view.qRadius.setText("%.6f" % parameters.quasar.radius.to(unitmap['qRadius']).value)
            self._view.qRedshift.setText("%.6f" % parameters.quasar.redshift)
            self._view.gRedshift.setText("%.6f" % parameters.galaxy.redshift)
            self._view.gVelDispersion.setText("%.6f" % parameters.galaxy.velocityDispersion.value)
            self._view.gNumStars.setText("%d" % int(parameters.galaxy.percentStars * 100))
            self._view.gShearMag.setText("%.6f" % parameters.galaxy.shearMag)
            self._view.gShearAngle.setText("%.6f" % parameters.galaxy.shearAngle.to('degree').value)
            self._view.scaleInput.setText("%.6f" % (parameters.dTheta.to(unitmap['scale']).value * parameters.canvasDim))
            self._view.dimensionInput.setText("%d" % parameters.canvasDim)
            self._view.quasarBHMassEntry.setText("%.6f" % parameters.quasar.mass.to('solMass').value)

    def toggle(self,state,read_only):
        self._view.paramFrame.setHidden(not self._view.paramFrame.isHidden())
        self.set_read_only(read_only)

    def get_units(self):
        qRadiusUnit = self._view.qRadiusUnitOption.currentText()
        qPosUnit = self._view.qPosUnit.currentText()
        qVelUnit = self._view.qVelocityUnit.currentText()
        scaleUnit = self._view.scaleUnitOption.currentText()
        gCenter = self._view.imgCenterLabel.currentText()
        ret =  {
        'qRadius':qRadiusUnit,
        'qPos':qPosUnit,
        'qVel':qVelUnit,
        'scale':scaleUnit,
        'center':gCenter
        }
        return ret