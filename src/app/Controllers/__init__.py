

def ControllerFactory(viewers,*signals):
    from app.Preferences import GlobalPreferences
    
    from . import Delegates
    from ..Models import Model
    from ..Views.LensedImageView import LensedImageView
    from ..Views.LightCurvePlotView import LightCurvePlotView
    from ..Views.MagMapView import MagMapView
    from .AnimationController import AnimationController
    from .CurveFileExporter import CurveFileExporter
    from .MasterController import MasterController


    masterController = AnimationController(*signals)
    noImgView = True
    for view in viewers:
        if isinstance(view,LensedImageView):
            noImgView = False
    if not GlobalPreferences['animate_motion']:
        masterController = MasterController(signals[0])
    modelView = {}
    for view in viewers:
        if view.modelID in Model:
            if view.modelID in modelView:
                modelView[view.modelID].append(view)
            else:
                modelView[view.modelID] = [view]
    for model,views in modelView.items():
        flag = False
        modelGetter = None
        fetcher = None
        for view in views:
            if isinstance(view,MagMapView):
                start = view.roiStartPos
                end = view.roiEndPos
                modelGetter = None
                fetcher = None
                if noImgView:
                    modelGetter = Delegates.MagMapLCGetter(model,start,end)
                    fetcher = Delegates.LightCurveFetcherDelegate()
                else:
                    modelGetter = Delegates.MagMapModelGetter(model,start,end)
                    fetcher = Delegates.MagnificationFetcherDelegate()
                flag = True
        if not flag:
            modelGetter = Delegates.TrajectoryModelGetter(model)
            fetcher = Delegates.PixelFetcherDelegate()
        masterController.addChild(modelGetter)
        modelGetter.addChild(fetcher)
        for view in views:
            if isinstance(view, LensedImageView):
                processor = Delegates.FrameDrawerDelegate()
                exporter = Delegates.FrameExporter(view.signal)
                fetcher.addChild(processor)
                processor.addChild(exporter)
            elif isinstance(view,LightCurvePlotView):
                processor = Delegates.CurveDrawerDelegate()
                exporter = Delegates.CurveExporter(view.signal)
                fetcher.addChild(processor)
                processor.addChild(exporter)
            elif isinstance(view,MagMapView):
                processor = Delegates.MagMapTracerDelegate()
                exporter = Delegates.MagMapTracerExporter(view.signal)
                fetcher.addChild(processor)
                processor.addChild(exporter)
    return masterController

def LightCurveExporterFactory(views,startSignal):
    from app.Preferences import GlobalPreferences
    
    from . import Delegates
    from ..Models import Model
    from ..Views.LensedImageView import LensedImageView
    from ..Views.LightCurvePlotView import LightCurvePlotView
    from ..Views.MagMapView import MagMapView
    from .AnimationController import AnimationController
    from .CurveFileExporter import CurveFileExporter
    from .MasterController import MasterController
    views = filter(lambda view: isinstance(view,MagMapView) or isinstance(view,LightCurvePlotView),views)
    filemanager = CurveFileExporter()
    masterController = MasterController(startSignal)
    masterController.filemanager = filemanager
    modelView = {}
    for view in views:
        if view.modelID in Model:
            if view.modelID in modelView:
                modelView[view.modelID].append(view)
            else:
                modelView[view.modelID] = [view]
    for model,views in modelView.items():
        fetcher = None
        for view in views:
            if isinstance(view,MagMapView):
                start = view.roiStartPos
                end = view.roiEndPos
                modelGetter = Delegates.MagMapLCGetter(model,start,end)
                masterController.addChild(modelGetter)
                fetcher = Delegates.LightCurveFetcherDelegate()
                modelGetter.addChild(fetcher)
                processor = Delegates.CurveDrawerDelegate()
                exporter = Delegates.CurveFileExporter()
                fetcher.addChild(processor)
                processor.addChild(exporter)
                filemanager.addSignal(exporter.signal)
    return masterController

def ExportFactory(views,startSignal):
    return LightCurveExporterFactory(views,startSignal)

