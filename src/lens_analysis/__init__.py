from lens_analysis.Experiment import Experiment
from lens_analysis.Trial import Trial
from lens_analysis.DirectoryMap import DirectoryMap
def load(filename):
    lngth = len(filename)
    if filename[lngth-4::] == '.dat':
        return Experiment(filename)
    else:
        return DirectoryMap(filename)
path = '../../ExperimentQueueTestFoler/'