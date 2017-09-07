
from .GUIController import GUIController

class MagMapTracerController(GUIController):


    def __init__(self,view):
        GUIController.__init__(self,view)


    def setMagmap(self,fileName = None, trialNum = 0):
        from .. import lens_analysis
        if fileName:
            magmap,params = lens_analysis.load(fileName)[trialNum].traceQuasar()
            self.magmapRaw = magmap.copy()
            center = params.extras.getParams('magmap').center.to('rad')
            engine = Engine_BruteForce()
            engine.updateParameters(params)
            baseMag = engine.query_raw_size(center.x,center.y,params.quasar.radius.to('rad').value)
            baseMag = engine.getMagnification(baseMag)
            baseMag = baseMag*255/magmap.max()
            magmap = np.array(magmap*255/magmap.max(),dtype=np.uint8)
            mag2 = magmap.copy()
            mag2[:,0] = magmap.shape[0] - magmap[:,0]
            mag2[:,1] = magmap[:,1]
            self.tracerView.setMagMap(mag2,baseMag)
            ModelImpl.updateParameters(params)
        else:
            paramsLoader = ParametersFileManager(self.view.signals)
            params = paramsLoader.read()
            magmap = self.fileManager.read()
            if not params or not magmap:
                return False
    #         self.view.bindFields(params)
            array = np.asarray(magmap.convert('YCbCr'))[:,:,0]
            self.tracerView.setMagMap(array)
            ModelImpl.updateParameters(params)

    
