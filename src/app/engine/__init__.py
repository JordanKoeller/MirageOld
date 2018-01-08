
from .CalculationDelegate import CalculationDelegate
from .PointerGridCalculationDelegate import PointerGridCalculationDelegate
from .ScalaSparkCalculationDelegate import ScalaSparkCalculationDelegate
from .MagMapCalculationDelegate import MagMapCalculationDelegate

from .Engine import Engine

Engine_PointerGrid = lambda: Engine(PointerGridCalculationDelegate())
Engine_ScalaSpark = lambda: Engine(ScalaSparkCalculationDelegate())

Engine_MagMap = lambda arg1, arg2, arg3: Engine(MagMapCalculationDelegate(arg1,arg2,arg3))

# from .Engine_PointerGrid import Engine_PointerGrid
# from .Engine_ScalaSpark import Engine_Spark as Engine_ScalaSpark
# # from .Engine_BruteForce import Engine_BruteForce as Engine_BruteForce
# from .Engine_MagMap import Engine_MagMap
# from .Engine import Engine
