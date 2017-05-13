from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

tree = Extension("Utility/SpatialTree_new", sources = ["Utility/SpatialTree_new.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries=["m"])
grid = Extension("Utility/Grid", sources = ["Utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
engine = Extension("Engine", sources = ["Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
engine_grid = Extension("Engine_Grid", sources = ["Engine_Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
engine_quadtree = Extension("Engine_Quadtree", sources = ["Engine_Quadtree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
engine_kdtree = Extension("Engine_KDTree", sources = ["Engine_KDTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
setup(
	ext_modules=cythonize([tree,engine,grid,engine_grid,engine_quadtree,engine_kdtree]),#,"Stellar/Galaxy.pyx"]),#,"Engine.pyx"]),
	include_dirs = [numpy.get_include()],
)
