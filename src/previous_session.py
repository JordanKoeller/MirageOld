from mirage import lens_analysis as la
from matplotlib import pyplot as plt
from scipy.stats import sigmaclip
from scipy.signal import argrelmax
from mirage.light_curves import *
from astropy import units as u
home_file = '/home/raqmu/Documents/Research/PeakComparison/10percent/large_sim/lightCurvesPlusMagmaps_20radiiForPeaks.dat'
get_ipython().run_line_magic('pylab', '')
all_ref_batch = LightCurveBatch([])
expts = la.load(home_file)
trial = expts[0]
parameters = trial.parameters
max_length = maximum_curve_length(parameters.quasar.angDiamDist.to('meter'))
curve_course = trial.lightcurves
reference_events = []
curves = curve_course.smooth_with_window(55)
print("First for loop")
j = 0
for i in range(len(curves)):
    curve = curves[i]
    curve.curve_id = i
    events = curve.get_events(2,151,u.Quantity(9,'uas'),u.Quantity(4,'uas'),10)
    for event in events:
        event.event_id = j
        event.curve_id = i
        j += 1
    slices = list(map(lambda x: x.slice_object,events))
    unfiltered = curve_course[i].get_slices(slices)
    unfiltered.curve_id = i
    for event in events:
        reference_events.append(event)
    # reference_events.append(events)
#Now construct a list of LightCurveBatches,
#Where each element represents a different quasar radius
#And each LightCurveBatch contains all the events for that radius.
list_of_events = [[]]*len(reference_events)
ts = list(map(lambda t: t.lightcurves,expts))
from mirage.light_curves.LightCurve import ProminenceChooser
chooser = ProminenceChooser()
def get_exact_peaks(y,num_peaks,x_threshold):
    print("New impl")
    indices = np.argsort(y)[::-1]
#    indices = np.sort(indices)
    trimmed = []
    trimmed.append(indices[0])
    i = 1
    while len(trimmed) < num_peaks and i < len(y):
        flag = True
        for peak in trimmed:
            if abs(peak - indices[i]) < x_threshold:
                flag = False
        if flag:
            trimmed.append(indices[i])
        i += 1
    return np.array(trimmed)
radii = np.linspace(5,40,20)
for i in range(len(reference_events)):
    tmp = [None] * 20
    slice_obj = reference_events[i].slice_object
    curve_id = reference_events[i].curve_id
    event_id = reference_events[i].event_id
    refe = reference_events[i]
    refe.num_peaks = chooser.find_peak_count(refe)
    top_peaks = get_exact_peaks(refe.curve,refe.num_peaks,50)
    refe.p1 = min(top_peaks)
    refe.p2 = max(top_peaks)
    for j in range(20):
        other_obj = ts[j][curve_id][slice_obj]
        other_obj.curve_id = curve_id
        other_obj.event_id = event_id
        other_obj.ref_num_peaks = refe.num_peaks
        other_obj.num_peaks = chooser.find_peak_count(other_obj)
        top_peaks = get_exact_peaks(other_obj.curve,other_obj.ref_num_peaks,50)
        other_obj.p1 = min(top_peaks)
        other_obj.p2 = max(top_peaks)
        other_obj.d1 = abs(refe.p1 - other_obj.p1)
        other_obj.d2 = abs(refe.p2 - other_obj.p2)
        other_obj.rad = radii[j]
        tmp[j] = other_obj
    lcb = LightCurveBatch(tmp)
    lcb.curve_id = curve_id
    lcb.event_id = event_id
    list_of_events[i] = lcb
tmp_for_df = []
c = 0
for vent in list_of_events:
    for e in vent:
        tup = [c,e.event_id,e.curve_id,e.ref_num_peaks,e.num_peaks,e.p1,e.p2,e.d1,e.d2,e.rad,len(e.curve),e.curve,e]
        tmp_for_df.append(tup)
        c += 1
import pandas as pd
headers = ["id","event-id","curve-id","ref_num_peaks","num_peaks","p1","p2","d1","d2","rad","len","plot","obj"]
df = pd.DataFrame(tmp_for_df,columns=headers)
d1 = df.copy()
d2 = df.copy()
d2['d1'] = d2['d2']
d2['event-id'] = - d2['event-id']
d2['p1'] = d1['p2']
master_df = d1.append(d2)
df2 = master_df[master_df['ref_num_peaks'] == 2]