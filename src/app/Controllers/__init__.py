from .AnimationController import AnimationController

from . import Delegates
from ..Views.LensedImageView import LensedImageView
from ..Views.LightCurvePlotView import LightCurvePlotView
from ..Models import Model

def ControllerFactory(viewers,*signals):
  modelView = {}
  for view in viewers:
    if view.modelID in modelView:
      modelView[view.modelID].append(view)
    else:
      modelView[view.modelID] = [view]
  masterController = AnimationController(*signals)
  for model,views in modelView.items():
    modelGetter = Delegates.TrajectoryModelGetter(model)

    masterController.addChild(modelGetter)
    fetcher = Delegates.PixelFetcherDelegate()

    for view in views:
      if isinstance(view, LensedImageView):
        processor = Delegates.FrameDrawerDelegate()
        exporter = Delegates.FrameExporter(view.signal)
        modelGetter.addChild(fetcher)
        fetcher.addChild(processor)
        processor.addChild(exporter)
      elif isinstance(view,LightCurvePlotView):
        processor = Delegates.CurveDrawerDelegate()
        exporter = Delegates.CurveExporter(view.signal)
        modelGetter.addChild(fetcher)
        fetcher.addChild(processor)
        processor.addChild(exporter)
  return masterController