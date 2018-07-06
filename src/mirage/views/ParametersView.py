'''
Created on Dec 23, 2017

@author: jkoeller
'''

import math
import random

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from astropy import constants as const
from astropy import units as u
from astropy.coordinates.representation import CartesianRepresentation
from astropy.coordinates.sky_coordinate import SkyCoord
import numpy as np

from mirage import parametersUIFile
from mirage.calculator import UnitConverter
from mirage.parameters import Parameters
from mirage.parameters.stellar import Galaxy, Quasar, EarthVelocity
from mirage.utility import Vector2D

from . import View
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget


class _ParametersViewWidget(GraphicsLayoutWidget):
    
    def __init__(self):
        GraphicsLayoutWidget.__init__(self)
        uic.loadUi(parametersUIFile, self)
        self._tmpStars = None
        
    def enableVelocityOptions(self, state=True):
        self.qPosLabel.setVisible(state)
        self.qPosUnit.setVisible(state)
        self.vel_label.setVisible(state)
        self.vel_units.setVisible(state)
        self.qVelocity.setVisible(state)
        self.qPositionEntry.setVisible(state)
        
    def _buildObjectHelper(self):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        returns them in a Parameters object.
        If the user inputs invalid arguments, will handle the error by returning None and sending a message
        to the progress_label_slot saying "Error. Input could not be parsed to numbers."
        """
        try:
            gRedshift = float(self.gRedshift.text())
            qRedshift = float(self.qRedshift.text())
            qBHMass = u.Quantity(float(self.quasarBHMassEntry.text()), 'solMass')
            specials = UnitConverter.generateSpecialUnits(qBHMass, qRedshift, gRedshift)
            with u.add_enabled_units(specials):
                # Setting units
                inputUnit = self.scaleUnitOption.currentText()
                # Determination of relative motion
                gVelocity = self.qVelocity.text()
                gComponents = gVelocity.strip('()').split(',')
                gPositionRaDec = self.gPositionEntry.text()
                apparentV = None
                if len(gComponents) == 2:
                    apparentV = self.vectorFromQString(self.qVelocity.text())
                else:
                    gVelocity = CartesianRepresentation(gComponents[0], gComponents[1], gComponents[2], '')
    
                    ra, dec = gPositionRaDec.strip('()').split(',')
                    gPositionRaDec = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
                    apparentV = self.getApparentVelocity(gPositionRaDec, gVelocity)
    
                # Quasar properties
                qPosition = self.vectorFromQString(self.qPosition.text(), unit='arcsec').to('rad')
                qRadius = u.Quantity(float(self.qRadius.text()), 'uas')
                
                # Galaxy properties
                gVelDispersion = u.Quantity(float(self.gVelDispersion.text()), 'km/s')
                gNumStars = int(self.gNumStars.text())
                gShearMag = float(self.gShearMag.text())
                gShearAngle = u.Quantity(float(self.gShearAngle.text()), 'degree')
                gStarStdDev = float(self.gStarStdDev.text())
                gStarMean = gVelDispersion
                gStarParams = None
                if gNumStars == 0 or gStarStdDev == 0:
                    gStarParams = None
                else:
                    gStarParams = (gStarMean, gStarStdDev)
                displayCenter = self.vectorFromQString(self.gCenter.text(), unit='arcsec').to('rad')
                dTheta = u.Quantity(float(self.scaleInput.text()), inputUnit).to('rad').value
                canvasDim = int(self.dimensionInput.text())
                if self._tmpStars:
                    galaxy = Galaxy(redshift=gRedshift,
                                    velocityDispersion=gVelDispersion,
                                    shearMag=gShearMag, shearAngle=gShearAngle,
                                    center=displayCenter,
                                    starVelocityParams=gStarParams,
                                    skyCoords=gPositionRaDec,
                                    velocity=gVelocity,
                                    stars=self._tmpStars[1])
                else:
                    galaxy = Galaxy(redshift=gRedshift,
                                    velocityDispersion=gVelDispersion,
                                    shearMag=gShearMag, shearAngle=gShearAngle,
                                    center=displayCenter,
                                    starVelocityParams=gStarParams,
                                    skyCoords=gPositionRaDec,
                                    velocity=gVelocity)
                quasar = Quasar(redshift=qRedshift,
                                radius=qRadius,
                                position=qPosition,
                                velocity=apparentV,
                                mass=qBHMass)
                params = Parameters(galaxy=galaxy,
                                    quasar=quasar,
                                    dTheta=dTheta,
                                    canvasDim=canvasDim)
                self._tmpStars = None
                if self.qRadiusUnitOption.currentIndex() == 1:
                    absRg = (params.quasar.mass * const.G / const.c / const.c).to('m')
                    angle = absRg / params.quasar.angDiamDist.to('m')
                    params.quasar.update(radius=u.Quantity(angle.value * qRadius.value, 'rad'))
                self.pixelAngleLabel_angle.setText(str(self._round_to_n(params.pixelScale_angle.value, 4)))
                self.pixelAngleLabel_thetaE.setText(str(self._round_to_n(params.pixelScale_thetaE, 4)))
                self.pixelAngleLabel_Rg.setText(str(self._round_to_n(params.pixelScale_Rg, 4)))
                self.quasarRadiusRGEntry.setText(str(self._round_to_n(params.quasarRadius_rg, 4)))
                return params
        except:
            print("Tried. Failed to build Parameters Instance")
            return False
    
    def getApparentVelocity(self, pos, v):
        ev = EarthVelocity
        apparentV = ev.to_cartesian() - v
        posInSky = pos.galactic
        phi, theta = (posInSky.l.to('rad').value, math.pi / 2 - posInSky.b.to('rad').value)
        vx = apparentV.x * math.cos(theta) * math.cos(phi) + apparentV.y * math.cos(theta) * math.sin(phi) - apparentV.z * math.sin(theta)
        vy = apparentV.y * math.cos(phi) - apparentV.x * math.sin(phi)
        ret = Vector2D(vx.value, vy.value, 'km/s')
        return ret

    def randomizeGVelocity(self):
        x, y, z = ((random.random() - 0.5) * 2, (random.random() - 0.5) * 2, (random.random() - 0.5) * 2)
        res = (x * x + y * y + z * z) ** (0.5)
        x /= res
        y /= res
        z /= res
        vel = np.array([x, y, z])
        vel = vel * (random.random() * 1e9)
        self.qVelocity.setText('(' + str(int(vel[0])) + "," + str(int(vel[1])) + "," + str(int(vel[2])) + ")")

    def _bindFieldsHelper(self, parameters):
        """Sets the User interface's various input fields with the data in the passed-in parameters object."""
        if parameters.stars != []:
            self._tmpStars = (parameters.galaxy.percentStars, parameters.galaxy.stars)
        else:
            self._tmpStars = None
        with u.add_enabled_units(parameters.specialUnits):
            qV = parameters.quasar.velocity.to('rad').unitless() * parameters.quasar.angDiamDist.to('km').value
            qP = parameters.quasar.position.to(self.qPositionLabel.text()).unitless()
            oqP = parameters.quasar.observedPosition.to(self.qPositionLabel.text()).unitless()
            gP = parameters.galaxy.position.to('arcsec').unitless()
#             self.qVelocity.setText(qV.asString)
            self.qPosition.setText(qP.asString)
            self.observedPosLabel.setText(oqP.asString)
            self.gCenter.setText(gP.asString)
            self.qRadius.setText(str(parameters.quasar.radius.to(self.qRadiusUnitOption.currentText()).value))
            self.qRedshift.setText(str(parameters.quasar.redshift))
            self.gRedshift.setText(str(parameters.galaxy.redshift))
            self.gVelDispersion.setText(str(parameters.galaxy.velocityDispersion.value))
            self.gNumStars.setText(str(int(parameters.galaxy.percentStars * 100)))
            self.gShearMag.setText(str(parameters.galaxy.shearMag))
            self.gShearAngle.setText(str(parameters.galaxy.shearAngle.to('degree').value))
            self.scaleInput.setText(str(parameters.dTheta.to(self.scaleUnitOption.currentText()).value * parameters.canvasDim))
            self.dimensionInput.setText(str(parameters.canvasDim))
            self.quasarBHMassEntry.setText(str(parameters.quasar.mass.to('solMass').value))
        
    def _round_to_n(self, x, n=6):
        '''
        round x to n many significant figures. Default is 6
        '''
        if x == 0.0:
            return 0
        else:
            return round(float(x), -int(math.floor(math.log10(abs(float(x))))) + (n - 1))

    def vectorFromQString(self, string, unit=None):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

        """
        x, y = (string.strip('()')).split(',')
        if ' ' in y:
            y = y.split(' ')[0]
        return Vector2D(float(x), float(y), unit)
    
    def _read_only(self, state):
        self.qVelocity.setReadOnly(state)
        self.qPosition.setReadOnly(state)
        self.gCenter.setReadOnly(state)
        self.qRadius.setReadOnly(state)
        self.qRedshift.setReadOnly(state)
        self.gRedshift.setReadOnly(state)
        self.gVelDispersion.setReadOnly(state)
        self.gNumStars.setReadOnly(state)
        self.gShearMag.setReadOnly(state)
        self.gShearAngle.setReadOnly(state)
        self.gPositionEntry.setReadOnly(state)
        self.gStarStdDev.setReadOnly(state)
        self.scaleInput.setReadOnly(state)
        self.dimensionInput.setReadOnly(state)
        self.quasarBHMassEntry.setReadOnly(state)
        self.regenerateStars.setDisabled(state)
        self.qVelRandomizer.setDisabled(state)
    

class ParametersView(View):
    '''
    classdocs
    '''
    
    _sendParameters = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        View.__init__(self, *args, **kwargs)
        self.widget = _ParametersViewWidget()
        self.addWidget(self.widget)
        self.addSignals(send_parameters=self._sendParameters,
                        regenerate_stars=self.widget.regenerateStars.clicked,
                        set_input_units=self.widget.scaleUnitOption.currentTextChanged)

    def update_slot(self, parameters):
        assert isinstance(parameters, Parameters)
        self._bindFieldsHelper(parameters)

    def enableVelocityOptions(self, state=True):
        return self.widget.enableVelocityOptions(state)
    
    def vectorFromQString(self, string, unit=None):
        return self.widget.vectorFromQString(string, unit)
    
    def _bindFieldsHelper(self, parameters):
        return self.widget._bindFieldsHelper(parameters)
        
    def getApparentVelocity(self, pos, v):
        return self.widget.getApparentVelocity(pos, v)
    
    def randomizeGVelocity(self):
        return self.widget.randomizeGVelocity()
    
    def _round_to_n(self, x, n=6):
        return self.widget._round_to_n(x, n)
    
    def _buildObjectHelper(self):
        return self.widget._buildObjectHelper()
    
    def getParameters(self):
        self.signals['send_parameters'].emit(self._buildObjectHelper())
        
    def set_read_only(self, state):
        self.widget._read_only(state)
