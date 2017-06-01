from Views.Drawer.Drawer import Drawer
from Views.Drawer.Drawer import PlotDrawer
from Views.Drawer.Drawer import ImageDrawer
from Views.Drawer.Drawer import CompositeDrawer
from Views.Drawer.LensedImageDrawer import LensedImageDrawer

def LensedImageLightCurveComposite(imgSignal, curveSignal):
	img = LensedImageDrawer(imgSignal)
	curve = PlotDrawer(curveSignal)
	return CompositeDrawer(img,curve)