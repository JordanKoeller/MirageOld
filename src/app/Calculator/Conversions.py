import numpy as np 
from ..Utility.Vec2D import Vector2D
# from ..Models import Model

def angleToPixel(angles,model):
    parameters = model.parameters
    canvasDim = parameters.canvasDim
    dTheta = parameters.dTheta.to('rad').value

    if isinstance(angles,np.ndarray):
        angles[:,0] = (angles[:,0]/dTheta)+canvasDim/2
        angles[:,1] = canvasDim/2 - (angles[:,1]/dTheta)
        return angles
    else:
        angles = angles.to('rad')/dTheta
        return Vector2D(angles.x+canvasDim/2,canvasDim/2 - angles.y)


def pixelToAngle(pixels,model):
    parameters = model.parameters
    canvasDim = parameters.canvasDim
    dTheta = parameters.dTheta.to('rad').value

    if isinstance(pixels, np.ndarray):
        pixels[:,0] = (pixels+canvasDim/2)*dTheta
        pixels[:,1] = (canvasDim/2 - pixels)*dTheta
        return pixels
    else:
        pixels = pixels*dTheta
        return Vector2D(pixels.x + canvasDim/2,canvasDim/2 - pixels.y)