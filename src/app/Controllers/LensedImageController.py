
from .GUIController import GUIController
from ..Utility.Vec2D import Vector2D, zeroVector
from ..Calculator import Conversions

class LensedImageController(GUIController):


    def __init__(self,view):
        GUIController.__init__(self,view)
        self.view = view
        self.view.sigPressed.connect(self.startListening)
        self.view.sigDragged.connect(self.updateCoords)
        self.view.sigReleased.connect(self.emitParamsUpdate)
        self._startPos = zeroVector
        self._currPos = zeroVector

    def startListening(self, pos):
        # print(model.parameters)
        self._startPos = Vector2D(pos.x(),pos.y())

    def updateCoords(self,pos):
        self._currPos = Vector2D(pos.x(),pos.y())

    def emitParamsUpdate(self, pos):
        from ..Models import Model
        model = Model[self.view.modelID]
        startAngle = Conversions.pixelToAngle(self._startPos,model)
        currAngle = Conversions.pixelToAngle(self._currPos,model)
        #NEEDS DEBUGGING HERE
        newMid = (currAngle+startAngle)/2.0
        newAngleWidth = startAngle - currAngle
        model.parameters.galaxy.update(center = newMid) #Smelly. Should be passable as *args, **kwargs
        print("NEWMID"+str(newMid))
        print("NEWDTHETA"+str(newAngleWidth))
        model.updateParameters(dTheta = newAngleWidth.magWithUnits())
        model.engine.reconfigure()
        # print(model.parameters)

    def buildObject(self,*args,**kwargs):
        print("SERIOUS SMELL HERE")
        from ..Models import Model
        return Model[self.view.modelID].parameters

    @property
    def modelID(self):
        return self.view.modelID
