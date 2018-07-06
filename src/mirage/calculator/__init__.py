import os


from .ExperimentTableRunner import ExperimentTableRunner

currDir = os.path.abspath(__file__)[0:-11]
gpu_kernel = open(currDir+'ray_tracer.cl')

def getMassFunction():
    from .InitialMassFunction import Kroupa_2001, Kroupa_2001_Modified, Weidner_Kroupa_2004, IMF_broken_powerlaw, Evolved_IMF, Seeding_Decorator
    import numpy as np
    from mirage.preferences import GlobalPreferences
    seed = GlobalPreferences['star_generator_seed']
    fn = GlobalPreferences['mass_function']
    ret = None
    if fn == "Kroupa_2001": ret = Seeding_Decorator(Kroupa_2001(),seed)
    elif fn == "Pooley_2011": ret = Seeding_Decorator(Kroupa_2001_Modified(),seed)
    elif fn == "Aged_galaxy": ret = Seeding_Decorator(Evolved_IMF(),seed)
    #Means this is a custom IMF. It may or may not have aging thresholds.
    elif "mass_limits" in fn and "powers" in fn:
        ret = Seeding_Decorator(IMF_broken_powerlaw(np.array(fn['mass_limits']),np.array(fn['powers'])),seed)
        if "conversions" in fn: ret = Seeding_Decorator(Evolved_IMF(ret,fn['conversions']),seed)
    if ret == None:
        raise ValueError("Not a valid mass function. Please update your preferences.")
    else:
        return ret

        


#Fully Documented package