from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

tree = Extension("SpatialTree", sources = ["SpatialTree.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
engine = Extension("Engine_cl", sources = ["Engine_cl.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
cEngineHelper = Extension("engineHelper", sources = ["engineHelper.pyx"], language="c", extra_compile_args=["-std=c99"], extra_link_args=["-std=c99"],libraries = ["m"])
setup(
	ext_modules=cythonize([engine,tree,cEngineHelper]),#,"stellar/Galaxy.pyx"]),#,"Engine.pyx"]),
	include_dirs = [numpy.get_include()],
)
