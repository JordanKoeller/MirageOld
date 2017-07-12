from .Drawer import Drawer
from .Drawer import PlotDrawer
from .Drawer import ImageDrawer
from .Drawer import CompositeDrawer
from .LensedImageDrawer import LensedImageDrawer
from ...Utility.NullSignal import NullSignal

def LensedImageLightCurveComposite(imgSignal=NullSignal, curveSignal=NullSignal):
	img = LensedImageDrawer(imgSignal)
	curve = PlotDrawer(curveSignal)
	return CompositeDrawer(img,curve)