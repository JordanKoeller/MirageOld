
from .CalculationDelegate import CalculationDelegate
from .PointerGridCalculationDelegate import PointerGridCalculationDelegate
from .ScalaSparkCalculationDelegate import ScalaSparkCalculationDelegate
from .MagMapCalculationDelegate import MagMapCalculationDelegate
from .Engine import Engine

Engine_PointerGrid = lambda: Engine(PointerGridCalculationDelegate())
Engine_ScalaSpark = lambda: Engine(ScalaSparkCalculationDelegate())

Engine_MagMap = lambda arg1, arg2, arg3: Engine(MagMapCalculationDelegate(arg1,arg2,arg3))

