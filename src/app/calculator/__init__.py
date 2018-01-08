import os


from .ExperimentTableRunner import ExperimentTableRunner
from .InitialMassFunction import Kroupa_2001, Kroupa_2001_Modified, Weidner_Kroupa_2004, IMF_broken_powerlaw, Evolved_IMF

currDir = os.path.abspath(__file__)[0:-11]
gpu_kernel = open(currDir+'ray_tracer.cl')

def setMassFunction(fn):
    import numpy as np
    ret = None
    if fn == "Kroupa_2001": ret = Kroupa_2001()
    elif fn == "Pooley_2011": ret = Kroupa_2001_Modified()
    elif fn == "Aged_galaxy": ret = Evolved_IMF()
    #Means this is a custom IMF. It may or may not have aging thresholds.
    elif "mass_limits" in fn and "powers" in fn:
        ret = IMF_broken_powerlaw(np.array(fn['mass_limits']),np.array(fn['powers']))
        if "conversions" in fn: ret = Evolved_IMF(ret,fn['conversions'])
    if ret == None:
        raise ValueError("Not a valid mass function. Please update your preferences.")
    else:
        global MassFunction
        MassFunction = ret
    
        

MassFunction = Kroupa_2001_Modified()

#Fully Documented package