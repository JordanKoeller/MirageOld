#Import my custom stuff
from mirage import lens_analysis as la
import mirage


#Import general things
from astropy import units as u
#from matplotlib import pyplot as plt

#A few ipython things to manipulate the environment
try:
    from IPython import get_ipython
    ipython = get_ipython()
    ipython.magic('pylab')
    #cleanup
    del(ipython)
    del(get_ipython)
except ImportError:
    print("Running without ipython")
    import numpy as np
    from math import *
    from numpy import *
    try:
        from matplotlib import pyplot as plt
    except:
        print("And without matplotlib")
