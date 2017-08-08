from .AnimationController import AnimationController

from . import Delegates
from ..Views.LensedImageView import LensedImageView
from ..Views.LightCurvePlotView import LightCurvePlotView
from ..Views.MagMapView import MagMapView
from ..Models import Model

def ControllerFactory(viewers,*signals):
    modelView = {}
    for view in viewers:
        if view.modelID in Model:
            if view.modelID in modelView:
                modelView[view.modelID].append(view)
            else:
                modelView[view.modelID] = [view]
    masterController = AnimationController(*signals)
    for model,views in modelView.items():
        flag = False
        modelGetter = None
        fetcher = None
        for view in views:
            if isinstance(view,MagMapView):
                start = view.roiStartPos
                end = view.roiEndPos
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