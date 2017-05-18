from Drawer.Drawer import Drawer
from Drawer.Drawer import PlotDrawer
from Drawer.Drawer import ImageDrawer
from Drawer.Drawer import CompositeDrawer
from Drawer.LensedImageDrawer import LensedImageDrawer

def LensedImageLightCurveComposite(imgSignal, curveSignal):
	img = LensedImageDrawer(imgSignal)
	curve = PlotDrawer(curveSignal)
	return CompositeDrawer(img,curve)