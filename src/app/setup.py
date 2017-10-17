


from distutils.core import setup, Extension

from Cython.Build import cythonize
import numpy


tree = Extension("Utility/SpatialTree_new", sources = ["Utility/SpatialTree_new.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries=["m"])
grid = Extension("Utility/Grid", sources = ["Utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
ptrgrid = Extension("Utility/PointerGrid", sources = ["Utility/PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
windowgrid = Extension("Utility/WindowGrid", sources = ["Utility/WindowGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
shapegrid = Extension("Utility/ShapeGrid", sources = ["Utility/ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11", "-funroll-loops"], extra_link_args=["-std=c++11", "-fopenmp"])
engine = Extension("Calculator/Engine/Engine", sources = ["Calculator/Engine/Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11", "-fopenmp"], libraries = ["m"])
engine_grid = Extension("Calculator/Engine/Engine_Grid", sources = ["Calculator/Engine/Engine_Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_magmap = Extension("Calculator/Engine/Engine_MagMap", sources = ["Calculator/Engine/Engine_MagMap.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_windowed = Extension("Calculator/Engine/Engine_Windowed", sources = ["Calculator/Engine/Engine_Windowed.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast","-fopenmp"], libraries = ["m"])
engine_ptrgrid = Extension("Calculator/Engine/Engine_PointerGrid", sources = ["Calculator/Engine/Engine_PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_bruteforce = Extension("Calculator/Engine/Engine_BruteForce", sources = ["Calculator/Engine/Engine_BruteForce.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp","-funroll-loops"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_shapegrid = Extension("Calculator/Engine/Engine_ShapeGrid", sources = ["Calculator/Engine/Engine_ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp","-funroll-loops"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_quadtree = Extension("Calculator/Engine/Engine_Quadtree", sources = ["Calculator/Engine/Engine_Quadtree.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
engine_kdtree = Extension("Calculator/Engine/Engine_KDTree", sources = ["Calculator/Engine/Engine_KDTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
drawer_supers = Extension("Views/Drawer/Drawer", sources = ["Views/Drawer/Drawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
drawer_curve = Extension("Views/Drawer/CurveDrawer_Tracer", sources = ["Views/Drawer/CurveDrawer_Tracer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("Views/Drawer/LensedImageDrawer", sources = ["Views/Drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("Views/Drawer/LensedImageDrawer", sources = ["Views/Drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
datavisdrawer = Extension("Views/Drawer/DataVisualizerDrawer", sources = ["Views/Drawer/DataVisualizerDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("Views/Drawer/ShapeDrawer", sources = ["Views/Drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("Views/Drawer/ShapeDrawer", sources = ["Views/Drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])

setup(
	ext_modules =cythonize([tree,
							grid,
							engine,
							ptrgrid,
							windowgrid,
							shapegrid,
							drawer_supers,
							datavisdrawer,
							engine_ptrgrid,
							lensedimgdrawer,
							engine_shapegrid,
							engine_bruteforce,
							engine_windowed,
							engine_magmap,
							shapedrawer]),
	include_dirs = [numpy.get_include(),"Utility"],
)
