


from distutils.core import setup, Extension

from Cython.Build import cythonize
import numpy


tree = Extension("utility/SpatialTree_new", sources = ["utility/SpatialTree_new.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries=["m"])
grid = Extension("utility/Grid", sources = ["utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
ptrgrid = Extension("utility/PointerGrid", sources = ["utility/PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
grid_wrapper = Extension("utility/GridWrapper", sources = ["utility/GridWrapper.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
windowgrid = Extension("utility/WindowGrid", sources = ["utility/WindowGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
shapegrid = Extension("utility/ShapeGrid", sources = ["utility/ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11", "-funroll-loops"], extra_link_args=["-std=c++11", "-fopenmp"])
engine = Extension("engine/Engine", sources = ["engine/Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11", "-fopenmp"], libraries = ["m"])
engine_grid = Extension("engine/Engine_Grid", sources = ["engine/Engine_Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_magmap = Extension("engine/Engine_MagMap", sources = ["engine/Engine_MagMap.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_windowed = Extension("engine/Engine_Windowed", sources = ["engine/Engine_Windowed.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast","-fopenmp"], libraries = ["m"])
engine_ptrgrid = Extension("engine/Engine_PointerGrid", sources = ["engine/Engine_PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_spark = Extension("engine/Engine_Spark", sources = ["engine/Engine_Spark.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_bruteforce = Extension("engine/Engine_BruteForce", sources = ["engine/Engine_BruteForce.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp","-funroll-loops"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_shapegrid = Extension("engine/Engine_ShapeGrid", sources = ["engine/Engine_ShapeGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp","-funroll-loops"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
engine_quadtree = Extension("engine/Engine_Quadtree", sources = ["engine/Engine_Quadtree.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
engine_kdtree = Extension("engine/Engine_KDTree", sources = ["engine/Engine_KDTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11","-fopenmp"], libraries = ["m"])
drawer_supers = Extension("views/drawer/Drawer", sources = ["views/drawer/Drawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
drawer_curve = Extension("views/drawer/CurveDrawer_Tracer", sources = ["views/drawer/CurveDrawer_Tracer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("views/drawer/LensedImageDrawer", sources = ["views/drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
lensedimgdrawer = Extension("views/drawer/LensedImageDrawer", sources = ["views/drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
datavisdrawer = Extension("views/drawer/DataVisualizerDrawer", sources = ["views/drawer/DataVisualizerDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("views/drawer/ShapeDrawer", sources = ["views/drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
shapedrawer = Extension("views/drawer/ShapeDrawer", sources = ["views/drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])

setup(
	ext_modules = cythonize([tree,
							grid,
							engine,
							ptrgrid,
							grid_wrapper,
#							windowgrid,
#							shapegrid,
							drawer_supers,
							datavisdrawer,
							engine_ptrgrid,
# 							engine_spark,
							lensedimgdrawer,
#							engine_shapegrid,
# 							engine_bruteforce,
# 							engine_windowed,
# 							engine_magmap,
							shapedrawer]),
	include_dirs = [numpy.get_include(),"utility"],
)
