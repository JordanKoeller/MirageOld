from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

tree = Extension("Utility/SpatialTree_new", sources = ["Utility/SpatialTree_new.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries=["m"])
grid = Extension("Utility/Grid", sources = ["Utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
engine = Extension("Engine", sources = ["Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
engine_grid = Extension("Engine_Grid", sources = ["Engine_Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_quadtree = Extension("Engine_Quadtree", sources = ["Engine_Quadtree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
engine_kdtree = Extension("Engine_KDTree", sources = ["Engine_KDTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
drawer_supers = Extension("Drawer/Drawer", sources = ["Drawer/Drawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("Drawer/LensedImageDrawer", sources = ["Drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
datavisdrawer = Extension("Drawer/DataVisualizerDrawer", sources = ["Drawer/DataVisualizerDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("Drawer/ShapeDrawer", sources = ["Drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
# curvedrawer = Extension("Drawer/CurveDrawer", sources = ["Drawer/CurveDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
# diagnosticdrawer = Extension("Drawer/DiagnosticDrawer", sources = ["Drawer/DiagnosticDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])

setup(
	ext_modules=cythonize([tree,engine,grid,engine_grid,engine_kdtree,drawer_supers,lensedimgdrawer,datavisdrawer,shapedrawer], nthreads = 8),
	include_dirs = [numpy.get_include()],
)
