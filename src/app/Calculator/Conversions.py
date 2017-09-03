import numpy as np 
from ..Utility.Vec2D import Vector2D
from ..Models.Model import Model

def angleToPixel(angles,parameters=None):
    """
    Provides simple conversions between angle measurements to pixel coordinates. angles can be a numpy array, or a Vector2D instance.
    If no parameters are supplied, uses default parameters
    """
    parameters = parameters or Model['default']
    canvasDim = parameters.canvasDim
    dTheta = parameters.dTheta.to('rad').value

    if isinstance(angles,np.ndarray):
        angles[:,0] = (angles[:,0]/dTheta)+canvasDim/2
        angles[:,1] = canvasDim/2 - (angles[:,1]/dTheta)
        return angles
    else:
        angles = angles.to('rad')/dTheta
        return Vector2D(angles.x+canvasDim/2,canvasDim/2 - angles.y)


def pixelToAngle(pixels,parameters=None):
    """
    Provides simple conversions between pixel coordinates and angle measurements. pixels can be a numpy array, or a Vector2D instance.
    If no parameters are supplied, uses default parameters
    """
    parameters = parameters or Model['default']
    canvasDim = parameters.canvasDim
    dTheta = parameters.dTheta.to('rad').value

    if isinstance(pixels, np.ndarray):
        pixels[:,0] = (pixels+canvasDim/2)*dTheta
        pixels[:,1] = (canvasDim/2 - pixels)*dTheta
        return pixels
    else:
        pixels = pixels*dTheta
        return Vector2D(pixels.x + canvasDim/2,canvasDim/2 - pixels.y)