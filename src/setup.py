


from distutils.core import setup, Extension

from Cython.Build import cythonize
import numpy

tree = Extension("Utility/SpatialTree_new", sources = ["Utility/SpatialTree_new.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries=["m"])
grid = Extension("Utility/Grid", sources = ["Utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
ptrgrid = Extension("Utility/PointerGrid", sources = ["Utility/PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
shapegrid = Extension("Utility/ShapeGrid", sources = ["Utility/ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
engine = Extension("Calculator/Engine/Engine", sources = ["Calculator/Engine/Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11", "-fopenmp"], libraries = ["m"])
engine_grid = Extension("Calculator/Engine/Engine_Grid", sources = ["Calculator/Engine/Engine_Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_ptrgrid = Extension("Calculator/Engine/Engine_PointerGrid", sources = ["Calculator/Engine/Engine_PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_shapegrid = Extension("Calculator/Engine/Engine_ShapeGrid", sources = ["Calculator/Engine/Engine_ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_quadtree = Extension("Calculator/Engine/Engine_Quadtree", sources = ["Calculator/Engine/Engine_Quadtree.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
engine_kdtree = Extension("Calculator/Engine/Engine_KDTree", sources = ["Calculator/Engine/Engine_KDTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
drawer_supers = Extension("Views/Drawer/Drawer", sources = ["Views/Drawer/Drawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("Views/Drawer/LensedImageDrawer", sources = ["Views/Drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
datavisdrawer = Extension("Views/Drawer/DataVisualizerDrawer", sources = ["Views/Drawer/DataVisualizerDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("Views/Drawer/ShapeDrawer", sources = ["Views/Drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
# curvedrawer = Extension("Views/Drawer/CurveDrawer", sources = ["Views/Drawer/CurveDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
# diagnosticdrawer = Extension("Views/Drawer/DiagnosticDrawer", sources = ["Views/Drawer/DiagnosticDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
setup(
	ext_modules=cythonize([tree,engine,grid,ptrgrid,shapegrid,engine_grid,engine_ptrgrid,engine_shapegrid,drawer_supers,lensedimgdrawer,datavisdrawer,shapedrawer], nthreads = 8),
	include_dirs = [numpy.get_include(),"Utility"],
)
