from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

# tree = Extension("Utility/SpatialTree", sources = ["Utility/SpatialTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
grid = Extension("Utility/Grid", sources = ["Utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
engine = Extension("Engine_cl", sources = ["Engine_cl.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
setup(
	ext_modules=cythonize([engine,grid]),#,"Stellar/Galaxy.pyx"]),#,"Engine.pyx"]),
	include_dirs = [numpy.get_include()],
)
