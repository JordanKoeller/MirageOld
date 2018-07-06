
from .CalculationDelegate import CalculationDelegate
from .PointerGridCalculationDelegate import PointerGridCalculationDelegate
from .ScalaSparkCalculationDelegate import ScalaSparkCalculationDelegate
from .MagMapCalculationDelegate import MagMapCalculationDelegate
from .Engine import Engine

Engine_PointerGrid = lambda: Engine(PointerGridCalculationDelegate())
Engine_ScalaSpark = lambda: Engine(ScalaSparkCalculationDelegate())

Engine_MagMap = lambda arg1, arg2, arg3: Engine(MagMapCalculationDelegate(arg1,arg2,arg3))

Engine_CPU = Engine_PointerGrid
Engine_Spark = Engine_ScalaSpark

def getCalculationEngine():
    from mirage.preferences import GlobalPreferences
    global CalculationModel
    if GlobalPreferences['calculation_device'] == 'cpu':
        return Engine_CPU()
    if GlobalPreferences['calculation_device'] == 'spark':
        return Engine_Spark()