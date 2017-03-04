from sympy import *

x = Symbol('x')
y = Symbol('y')
rx = Symbol('rx')
ry = Symbol('ry')
kSIS = Symbol('kSIS')
thetaGamma = Symbol('thetaGamma')
gamma = Symbol('gamma')

phi = kSIS*sqrt((theta[0]-rx)**2+(theta[1]-ry)**2) + (gamma/2)*((theta[0]-rx)**2+(theta[1]-ry)**2)*cos(2*(atan(theta[1]/theta[0])-thetaGamma))

dPhidX = diff(phi,x)
dPhi2dX2 = diff(dPhidX,x)
dPhidY = diff(phi,y)
dPhi2dY2 = diff(dPhidX,y)
dPhi2dXdY = diff(dPhidX,y)
dPhi2dYdX = diff(dPhidY,x)

hessianDet = dPhi2dX2*dPhi2dY2 - dPhi2dXdY*dPhi2dYdX