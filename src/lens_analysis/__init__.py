from lens_analysis.AbstractFileWrapper import AbstractFileWrapper
from lens_analysis.DirectoryMap import DirectoryMap
from lens_analysis.Experiment import Experiment
from lens_analysis.Trial import Trial


def load(filename):
    lngth = len(filename)
    if filename[lngth-4::] == '.dat':
        return Experiment(filename)
    else:
        return DirectoryMap(filename)

def describe(filename):
    if isinstance(filename, str):
        tmp = load(filename)
        tmp.describe
    else:
        try:
            filename.describe 
        except AttributeError:
            raise AttributeError("argument must be a filename or AbstractFileWrapper subtype.")
        
def explore(expt):
    pass
