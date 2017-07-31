from .AnimationController import AnimationController

from . import Delegates
from ..Views.LensedImageView import LensedImageView
from ..Views.LightCurvePlotView import LightCurvePlotView

# def ControllerFactory(views):
#     for view in views:
#         if isinstance(view,LensedImageView):


#         masterController = AnimationController()


#         modelGetter = Delegates.TrajectoryParametersGetter()

#         fetcher = Delegates.PixelFetcherDelegate()

#         processor = Delegates.FrameDrawerDelegate()
#         processor2 = Delegates.CurveDrawerDelegate()

#         exporter = Delegates.FrameExporter(views[0].signal)
#         exporter2 = Delegates.CurveExporter(views[1].signal)


#         masterController.addChild(modelGetter)
#         modelGetter.addChild(fetcher)
#         fetcher.addChild(processor)
#         fetcher.addChild(processor2)
#         processor.addChild(exporter)
#         processor2.addChild(exporter2)
#         processor2.addChild(exporter3)


#         return masterController
#         

def ControllerFactory(views,*signals):
  masterController = AnimationController(*signals)
  modelGetter = Delegates.TrajectoryParametersGetter()

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