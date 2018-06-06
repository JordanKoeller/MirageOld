'''
Created on Dec 19, 2017

@author: jkoeller
'''

import math
from astropy import units as u
from astropy.coordinates import SphericalRepresentation as SR
from astropy.coordinates import CartesianRepresentation as CR
from astropy.cosmology import WMAP7 as cosmo
import numpy as np

from ..calculator import Conversions
from ..utility.ParametersError import ParametersError
from ..utility import zeroVector, Vector2D, Vector2DJSONDecoder
from ..drawer.ShapeDrawer import drawPointLensers, drawCircle, drawSolidCircle, drawSquare
from ..utility import QuantityJSONEncoder, QuantityJSONDecoder

EarthVelocity = SR(u.Quantity(265, 'degree'), u.Quantity(48, 'degree'), 365)


class GalaxyJSONEncoder(object):
    """
    Provides a way to convert a Galaxy class instance into a json representation."""

    def __init__(self):
        super(GalaxyJSONEncoder, self).__init__()

    def encode(self, o):
        if isinstance(o, Galaxy):
            quantDecoder = QuantityJSONEncoder()
            res = {}
            res['position'] = o.center.jsonString
            res['velocityDispersion'] = quantDecoder.encode(o.velocityDispersion)
            res['redshift'] = o.redshift
            res['shearAngle'] = quantDecoder.encode(o.shearAngle)
            res['shearMag'] = o.shearMag
            m, x, y = o.starArray
            # res['starMasses'] = m.tolist()
            # res['starXPos'] = x.tolist()
            # res['starYPos'] = y.tolist()
            x = quantDecoder.encode(o.velocity.x)
            y = quantDecoder.encode(o.velocity.y)
            z = quantDecoder.encode(o.velocity.z)
            res['velocity'] = {'x':x, 'y':y, 'z':z}
            res['pcntStars'] = o.percentStars
            # res['skyCoords'] = o.skyCoords #WILL NEED HELP HERE
            res['avgStarMass'] = o.averageStarMass
            return res
        else:
            raise TypeError("parameter o must be Galaxy instance.")


class GalaxyJSONDecoder(object):
    """docstring for GalaxyJSONDecoder"""

    def __init__(self):
        super(GalaxyJSONDecoder, self).__init__()
        
    def decode(self, js):
        vd = Vector2DJSONDecoder()
        qd = QuantityJSONDecoder()
        position = vd.decode(js['position'])
        velD = qd.decode(js['velocityDispersion'])
        redshift = js['redshift']
        shearAngle = qd.decode(js['shearAngle'])
        shearMag = js['shearMag']
        # starm = js['starMasses']
        # starx = js['starXPos']
        # stary = js['starYPos']
        vx = qd.decode(js['velocity']['x'])
        vy = qd.decode(js['velocity']['y'])
        vz = qd.decode(js['velocity']['z'])
        velocity = CR(vx, vy, vz)
        pcntStars = js['pcntStars'] / 100
        # skyCoords = #NEED HELP HERE
        # if len(starm) > 0:
        #     stars = np.ndarray((len(starm), 3))
        #     stars[:0] = starm
        #     stars[:1] = starx
        #     stars[:2] = stary
        #     return Galaxy(redshift=redshift,
        #                   velocityDispersion=velD,
        #                   shearMag=shearMag,
        #                   shearAngle=shearAngle,
        #                   percentStars=pcntStars,
        #                   center=position,
        #                   velocity=velocity,
        #                   stars=stars)
        # else:
        return Galaxy(redshift=redshift,
                      velocityDispersion=velD,
                      shearMag=shearMag,
                      shearAngle=shearAngle,
                      percentStars=pcntStars,
                      center=position,
                      velocity=velocity)


class QuasarJSONEncoder(object):
    """Provides a way to convert a Quasar class instance into a json representation."""

    def __init__(self):
        super(QuasarJSONEncoder, self).__init__()
    
    def encode(self, o):
        if isinstance(o, Quasar):
            quantDecoder = QuantityJSONEncoder()
            res = {}
            res['position'] = o.position.jsonString
            res['mass'] = quantDecoder.encode(o.mass)
            res['velocity'] = o.velocity.jsonString
            res['observedPosition'] = o.observedPosition.jsonString
            res['radius'] = quantDecoder.encode(o.radius)
            res['redshift'] = o.redshift
            res['colorKey'] = o.colorKey
            return res
        else:
            raise TypeError("parameter o must be a Quasar instance.")


class QuasarJSONDecoder(object):
    """docstring for QuasarJSONDecoder"""

    def __init__(self):
        super(QuasarJSONDecoder, self).__init__()
        
    def decode(self, js):
        vd = Vector2DJSONDecoder()
        qd = QuantityJSONDecoder()
        position = vd.decode(js['position'])
        mass = qd.decode(js['mass'])
        velocity = vd.decode(js['velocity'])
        redshift = js['redshift']
        tmpCosmic = Cosmic()
        tmpCosmic.updateCosmic(redshift=redshift)
        velocity = (velocity * tmpCosmic.angDiamDist.to('m').value).setUnit('km/s')
        radius = qd.decode(js['radius'])
        return Quasar(redshift=redshift,
                      radius=radius,
                      position=position,
                      velocity=velocity,
                      mass=mass)


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

    def updateCosmic(self, **kwargs):
        for key, value in kwargs.items():
            try:
                getattr(self, "_Cosmic__" + key)
                if value != None:
                    setattr(self, "_Cosmic__" + key, value)
            except AttributeError:
                raise ParametersError("failed to update " + key + " in Cosmic")

    def cosmicString(self):
        return "redshift = " + str(self.redshift) + "\nAngDiamDist = " + str(self.angDiamDist)


class Drawable(object):
    __position = zeroVector
    __colorKey = 0
    
    def __init__(self):
        pass

    def draw(self, img, parameters):
        """Draws the entity to the canvas.
        Args:
            img - QImage to be drawn to.
            parameters - Configs class instance, specifying how to draw the entity.
        """

    def updateDrawable(self, **kwargs):
        for key, value in kwargs.items():
            try:
                getattr(self, "_Drawable__" + key)
                if value != None:
                    setattr(self, "_Drawable__" + key, value)
            except AttributeError:
                raise ParametersError("failed to update " + key + " in Drawable")

    def setPos(self, position):
        self.__position = position

    @property
    def position(self):
        return self.__position.to('rad')

    @property
    def colorKey(self):
        return self.__colorKey

    def drawableString(self):
        return "postion = " + str(self.position)


class Movable(Drawable):
    '''
    classdocs
    '''

    __observedPosition = zeroVector
    __velocity = zeroVector
    
    def __init__(self, position, velocity):
        '''
        Constructor
        '''
        super(Movable, self).__init__()
        self.__velocity = velocity
        self.__observedPosition = position
        
    @property
    def velocity(self):
        return self.__velocity.to('rad')

    def updateMovable(self, position, velocity):
        if velocity != None:
            self.__velocity = velocity
        if position:
            self.__observedPosition = position
            self._Drawable__position = position
        
#     @property
#     def position(self):
#         return self.__observedPosition.to('rad')
    
    @property
    def observedPosition(self):
        return self.__observedPosition.to('rad')

    def setTime(self, t):
        self.__observedPosition = self._Drawable__position + (self.velocity * t)

    def incrementTime(self, dt):
        self.__observedPosition = self.__observedPosition + self.velocity * dt

    def setPos(self, x, y=None):
        if y == None:
            self.__observedPosition = x
        else:
            self.__observedPosition = Vector2D(x, y)


class PointLenser(Movable):
    __mass = 0

    def __init__(self, position=None, mass=u.Quantity(0), velocity=zeroVector):
        Movable.__init__(self, position, velocity)
        self.__mass = mass 
        self.updateDrawable(position=position, colorKey=2)

    def __eq__(self, other):
        if other == None:
            return False
        if self.position != other.position:
            return False
        if self.mass != other.mass:
            return False
        if self.colorKey != other.colorKey:
            return False
        return True

    def __neq__(self, other):
        return not self.__eq__(other)

    def draw(self, img, parameters):
        center = (self.position) / parameters.dTheta.value
        center = Vector2D(int(center.x + parameters.canvasDim / 2), int(center.y + parameters.canvasDim / 2))
        radius = int(math.sqrt(self.mass.value + 2))
        drawSolidCircle(int(center.x), int(center.y), radius, img)

    @property
    def mass(self):
        return self.__mass.to('solMass')
    
    def drawSolidCircle(self, x0, y0, r, canvas):
        rSquared = r * r
        canvasDim = canvas.shape[0]    
        for x in range(0, r + 1):
            for y in range(0, r + 1):
                if x * x + y * y <= rSquared:
                    if x0 + x > 0 and y0 + y > 0 and x0 + x < canvasDim and y0 + y < canvasDim:
                        canvas[x0 + x, y0 + y] = 3
                    if x0 + x > 0 and y0 - y > 0 and x0 + x < canvasDim and y0 - y < canvasDim:
                        canvas[x0 + x, y0 - y] = 3
                    if x0 - x > 0 and y0 + y > 0 and x0 - x < canvasDim and y0 + y < canvasDim:
                        canvas[x0 - x, y0 + y] = 3
                    if x0 - x > 0 and y0 - y > 0 and x0 - x < canvasDim and y0 - y < canvasDim:
                        canvas[x0 - x, y0 - y] = 3


class Quasar(Movable, Cosmic):
    __radius = 0

    def __init__(self, redshift=2, radius=u.Quantity(1e6, 'uas'), position=Vector2D(0, 0, 'rad'),
                 mass=u.Quantity(1e9, 'solMass'), velocity=Vector2D(0, 0, 'km/s')):
        self.__radius = radius
        self.updateCosmic(redshift=redshift)
        normVel = velocity.to('km/s') / self.angDiamDist.to('km').value
        self.updateMovable(position=position, velocity=normVel.setUnit('rad'))
        self.updateDrawable(position=position, colorKey=3)
        self.__mass = mass

    def update(self, redshift=None, position=None, radius=None, velocity=None):
        try:
            self.updateCosmic(redshift=redshift)
            self.updateDrawable(position=position)
            self.updateMovable(position, velocity)
            if radius != None:
                try:
                    self.__radius = radius.to('rad')
                except:
                    raise ParametersError("Quasar radius must be an astropy.units.Quantity of angle units.")
        except ParametersError as e:
            raise e

    def draw(self, img, model):
        center = Conversions.angleToPixel(self.observedPosition, model)
        radius = int(self.radius.value / model.parameters.dTheta.value)
        if img.ndim == 3:
            drawSolidCircle(int(center.x), int(center.y), radius, img, self.colorKey, model)
        else:
            drawSolidCircle(int(center.x), int(center.y), radius, img, self.colorKey, model)

    def pixelRadius(self, dTheta):
        return (self.__radius.to('rad') / dTheta).value

    @property
    def radius(self):
        return self.__radius.to('rad')
    
    @property
    def mass(self):
        return self.__mass

    @property
    def jsonString(self):
        encoder = QuasarJSONEncoder()
        return encoder.encode(self)
    
    def __eq__(self, other):
        assert isinstance(other, Quasar), "Cannot compare a Quasar to an object of type " + str(type(other))
        return self.radius == other.radius and self.mass == other.mass and self.position == other.position and self.velocity == other.velocity and self.radius == other.radius
            
    def __str__(self):
        return "QUASAR:\n" + self.cosmicString() + "\n" + self.drawableString() + "\nvelocity = " + str(self.velocity) + "\nradius = " + str(self.radius) + "\n\n"


class ShearLenser(object):
    __mag = 0
    __angle = 0

    def __init__(self, mag, angle):
        self.__mag = mag
        self.__angle = angle

    def update(self, mag=None, angle=None):
        if mag != None:
            if isinstance(mag, float) or isinstance(mag, int):
                self.__mag = mag
            else:
                raise ParametersError("Shear Magnification must be a numeric type")
        if angle != None:
            try:
                self.__angle = angle.to('rad')
            except:
                raise ParametersError("Shear angle must be an instance of a astropy.units.Quantity, measuring angle.")

    def __eq__(self, other):
        if other == None:
            return False
        return self.magnitude == other.magnitude and self.angle == other.angle

    def __neq__(self, other):
        return not self.__eq__(other)

    def unscaledAlphaAt(self, position):
        pass

    @property
    def magnitude(self):
        return self.__mag

    @property
    def angle(self):
        return self.__angle.to('rad')

    def shearString(self):
        return "shearMag = " + str(self.magnitude) + "\nshearAngle = " + str(self.angle)


class Galaxy(Drawable, Cosmic):
    __velocityDispersion = u.Quantity(0, 'km/s')
    __pcntStar = 0
    __shear = None
    __stars = []

    def __init__(self, redshift=0.5, velocityDispersion=u.Quantity(1500, 'km/s'), shearMag=0.306,
                 shearAngle=u.Quantity(30, 'degree'), percentStars=0.0,
                 center=zeroVector.setUnit('rad'), velocity=u.Quantity(0, 'km/s'),
                 starVelocityParams=None, skyCoords=None, stars=[]):
        Drawable.__init__(self)
        Cosmic.__init__(self)
        self.__velocityDispersion = velocityDispersion
        self.__pcntStar = percentStars / 100
        self.__shear = ShearLenser(shearMag, shearAngle)
        self.updateDrawable(position=center, colorKey=4)
        self.updateCosmic(redshift=redshift)
        self.__starVelocityParams = starVelocityParams
        self.__avgStarMass = 0.5
        self.skyCoords = skyCoords
        self.velocity = velocity
        self.__stars = stars

    def drawStars(self, img, model):
        if len(self.__stars) != 0:
            if img.ndim == 3:
                drawPointLensers(self.__stars, img, model)
            else:
                drawPointLensers(self.__stars, img, model)

    def drawGalaxy(self, img, model):
        center = Conversions.angleToPixel(self.position, model)
        if img.ndim == 3:
            drawSquare(int(center.x), int(center.y), 5, img, self.colorKey, model)
        else:
            drawSquare(int(center.x), int(center.y), 5, img, self.colorKey, model)

    @property
    def starArray(self):
        if len(self.__stars) > 0:
            massArr = self.__stars[:, 2]
            xArr = self.__stars[:, 0]
            yArr = self.__stars[:, 1]
            return (massArr, xArr, yArr)    
        else:
            return ([], [], [])
            
    @property
    def starVelocityParams(self):
        return self.__starVelocityParams
        
    def clearStars(self):
        self.__stars = []
        self.__avgStarMass = 0.5
            
    def moveStars(self, dt):
        self.__stars[:, 0] = self.__stars[:, 0] + self.__stars[:, 3] * dt
        self.__stars[:, 1] = self.__stars[:, 1] + self.__stars[:, 4] * dt
            
    def update(self, redshift=None, velocityDispersion=None, shearMag=None, shearAngle=None, center=None, percentStars=None, stars=[]):
        try:
            self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
            self.__shear.update(shearMag, shearAngle)
            if percentStars != None:
                self.__pcntStar = percentStars / 100
            if stars != []:
                self.__stars = stars
                self.__avgStarMass = sum(stars[:, 2]) / len(stars)
            self.updateDrawable(position=center)
            self.updateCosmic(redshift=redshift)
        except ParametersError as e:
            raise e

    def __str__(self):
        return "GALAXY:\n" + self.drawableString() + "\n" + self.cosmicString() + "\n" + self.shear.shearString() + "\nvelocity Dispersion = " + str(self.velocityDispersion) + "\nnumStars = " + str(self.numStars) + "\n\n"

    def __eq__(self, other):
        if self.isSimilar(other) and self.__stars == other.stars:
            return True
        else:
            return False
    
    def isSimilar(self, other):
        if other == None:
            return False
        if self.redshift != other.redshift:
            return False
        if self.percentStars != other.percentStars:
            return False
        if self.shear != other.shear:
            return False
        if self.center.to('arcsec') != other.center.to('arcsec'):
            return False
        if self.velocityDispersion != other.velocityDispersion:
            return False
        return True

    @property
    def velocityDispersion(self):
        return self.__velocityDispersion.to('km/s')

    @property
    def percentStars(self):
        return self.__pcntStar

    @property
    def shear(self):
        return self.__shear

    @property
    def shearMag(self):
        return self.__shear.magnitude

    @property
    def shearAngle(self):
        return self.__shear.angle

    @property
    def numStars(self):
        return len(self.__stars)

    @property
    def center(self):
        return self.position

    @property
    def stars(self):
        return self.__stars
    
    @property
    def averageStarMass(self):
        return self.__avgStarMass

    @property
    def apparentVelocity(self):
        relVel = self.velocity - EarthVelocity    
        rCart = relVel.to_cartesian()
        l, b = (self.skyCoords.galactic.l, self.skyCoords.galactic.b.to('rad'))
        theta, phi = (math.pi / 2 - b, l)
        capTheta = rCart.x * math.cos(theta) * math.cos(phi) + rCart.y * math.cos(theta) * math.sin(phi) - rCart.z * math.sin(theta)
        capPhi = rCart.y * math.cos(phi) - rCart.x * math.sin(phi)
        return Vector2D(capTheta, capPhi, 'km/s')

    @property
    def jsonString(self):
        encoder = GalaxyJSONEncoder()
        return encoder.encode(self)


defaultGalaxy = Galaxy(redshift=0.0073,
    velocityDispersion=u.Quantity(1500, "km/s"),
    shearMag=0.3206,
    shearAngle=u.Quantity(30, 'degree'))

microGalaxy = Galaxy(redshift=0.0073,
    velocityDispersion=u.Quantity(1500, "km/s"),
    shearMag=0.3206,
    shearAngle=u.Quantity(30, 'degree'))

defaultQuasar = Quasar(redshift=0.073,
    position=Vector2D(-0.0003, 0, "rad"),
    radius=u.Quantity(5, "arcsecond"),
    velocity=Vector2D(0, 0, "km/s"))

microQuasar = Quasar(redshift=0.073,
    position=Vector2D(0, 0, "rad"),
    radius=u.Quantity(1.7037e-6, "rad"),
    velocity=Vector2D(1.59016e-8, 0, "km/s"))

