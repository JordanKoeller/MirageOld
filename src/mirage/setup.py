


from distutils.core import setup, Extension

from Cython.Build import cythonize
import numpy


if __name__ =="__main__":
	grid = Extension("utility/Grid", sources = ["utility/Grid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
	ptrgrid = Extension("utility/PointerGrid", sources = ["utility/PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"])
	engine = Extension("engine/Engine", sources = ["engine/Engine.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11", "-fopenmp"], libraries = ["m"])
	engine_magmap = Extension("engine/Engine_MagMap", sources = ["engine/Engine_MagMap.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
	engine_ptrgrid = Extension("engine/Engine_PointerGrid", sources = ["engine/Engine_PointerGrid.pyx"], language = "c++",    extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-Ofast"], libraries = ["m"])
	calcDel = Extension("engine/CalculationDelegate", sources = ["engine/CalculationDelegate.pyx"], language = "c++", extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-fopenmp"], libraries=["m"])
	ptrCalcDel = Extension("engine/PointerGridCalculationDelegate", sources = ["engine/PointerGridCalculationDelegate.pyx"], language = "c++", extra_compile_args=["-std=c++11","-fopenmp"], extra_link_args=["-std=c++11","-fopenmp"], libraries=["m"])
	rayTracerDel = Extension("engine/RayTracerDelegate", sources = ["engine/RayTracerDelegate.pyx"], language = "c++", libraries = ["m"])
	drawer_supers = Extension("drawer/Drawer", sources = ["drawer/Drawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	drawer_curve = Extension("drawer/CurveDrawer_Tracer", sources = ["drawer/CurveDrawer_Tracer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	lensedimgdrawer = Extension("drawer/LensedImageDrawer", sources = ["drawer/LensedImageDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	datavisdrawer = Extension("drawer/DataVisualizerDrawer", sources = ["drawer/DataVisualizerDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	shapedrawer = Extension("drawer/ShapeDrawer", sources = ["drawer/ShapeDrawer.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	peak_slicing = Extension("light_curves/peak_finding", sources = ["light_curves/peak_finding.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])
	raw_magCalc = Extension("calculator/RawMagCalculator", sources = ["calculator/RawMagCalculator.pyx"], language = "c++",    extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"], libraries = ["m"])

	setup(
		ext_modules = cythonize([
								grid,
								ptrgrid,
								calcDel,
								ptrCalcDel,
								drawer_supers,
								datavisdrawer,
								lensedimgdrawer,
								shapedrawer,
                                                                peak_slicing,
                                                                raw_magCalc]),
		include_dirs = [numpy.get_include(),"utility","drawer", "engine", "light_curves"],
	)
