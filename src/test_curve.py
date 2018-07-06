from mirage import lens_analysis as la
from matplotlib import pyplot as plt
from scipy.stats import sigmaclip
from mirage.light_curves import *
home_file = '/home/raqmu/Documents/Research/PeakComparison/10percent/large_sim/lightCurvesPlusMagmaps_20radiiForPeaks.dat'

print("Running Test")
trial = la.load(home_file,0)
curve = trial.lightcurves[9]
curves = trial.lightcurves
events = curve.get_event_slices(3,1.5,tail_factor=0.0)
for i in range(10,20):
    curve = curves[i]
    events = events + curve.get_event_slices(3,1.5,tail_factor=0.0)
print("Now on to classifying")
classified = LightCurveClassificationTable(events,0.8,method="PeakCounting")
classified.describe()

print("Done")
