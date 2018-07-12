# coding: utf-8
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
max_length = maximum_curve_length(parameters.quasar.angDiamDist.to('meter').value)
curve_course = trial.lightcurves
reference_events = []
curves = curve_course.smooth_with_window(55)
print("First for loop")
for i in range(len(curves)):
    curve = curves[i]
    curve.curve_id = i
    events = curve.get_events(2,151,u.Quantity(9,'uas'),u.QUantity(4,'uas'),10)
    events = list(map(lambda x: x.trimmed_to_size(max_length),events))
    slices = list(map(lambda x: x.slice_object,events))
    unfiltered = curve_course[i].get_slices(slices)
    unfiltered.curve_id = i
    reference_events.append(events)
#Now construct a list of LightCurveBatches,
#Where each element represents a different quasar radius
#And each LightCurveBatch contains all the events for that radius.
list_of_events = [None]*20
print("Second for loop")
for trial_number in range(20):
    batch_for_radius = LightCurveBatch([])
    trial = expts[trial_number]
    trial_curves = trial.lightcurves
    for reference_curveI in range(len(reference_events)):
        reference_batch = reference_events[reference_curveI]
        reference_batch.curve_id = reference_curveI
        reference_slices = list(map(lambda x: x.slice_object,reference_batch))
        curr_radius_line = trial_curves[reference_curveI]
        curr_radius_line.curve_id = reference_curveI
        curr_radius_line.trial_id = trial_number
        events_in_r = curr_radius_line.get_slices(reference_slices)
        batch_for_radius = batch_for_radius + events_in_r
        batch_for_radius.trial_id = trial_number
    list_of_events[trial_number] = batch_for_radius
#So each element of list_of_events is a LightCurveBatch, with all the events
#At the radius indicated by the index of the element in list_of_events,
#In the same order
for group in reference_events:
    all_ref_batch = all_ref_batch + group
table = LightCurveClassificationTable(all_ref_batch,1e-10,method='Prominence')
grouped_by_event = []
double_horns = table[0]
trials = list(map(lambda t:t.lightcurves,expts))
print("In Double Horns")
for sliced_event in double_horns:
    all_radii_of_event = []
    curve_id = sliced_event.parent_curve.curve_id
    slice_obj = sliced_event.slice_object
    for i in range(0,20):
        lightcurves = trials[i]
        curve = lightcurves[curve_id]
        curve.curve_id = curve_id
        sliced = curve[slice_obj]
        all_radii_of_event.append(sliced)
    grouped_by_event.append(all_radii_of_event)
import pickle
def save_pickled(fname,obj):
    with open(fname,'wb+') as f:
        pickle.dump(obj,f)
shift_array = np.ndarray((len(grouped_by_event),20))
from mirage.light_curves.peak_finding import prominences
def argTopTwoPeaks(curve):
    possible, = argrelmax(curve)
    if len(possible) == 0:
        return [np.nan,np.nan]
    elif len(possible) == 1:
        return [possible[0],np.nan]
    else:
        proms = prominences(curve,possible)
        top_two = np.argpartition(proms,len(proms) - 1)[-2:]
        return [possible[top_two[0]],possible[top_two[1]]]
print("Grouping")
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        shift_array[eventI,radiusI] = first_peak - first_corr
print("Describing")
from scipy.stats import describe
abs_arr = abs(shift_array)
stats = describe(abs_arr,nan_policy='omit')
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
for i in range(len(curves)):
    curve = curves[i]
    curve.curve_id = i
    events = curve.get_events(2,151,u.Quantity(9,'uas'),u.Quantity(4,'uas'),10)
    events = list(map(lambda x: x.trimmed_to_size(max_length),events))
    slices = list(map(lambda x: x.slice_object,events))
    unfiltered = curve_course[i].get_slices(slices)
    unfiltered.curve_id = i
    reference_events.append(events)
#Now construct a list of LightCurveBatches,
#Where each element represents a different quasar radius
#And each LightCurveBatch contains all the events for that radius.
list_of_events = [None]*20
print("Second for loop")
for trial_number in range(20):
    batch_for_radius = LightCurveBatch([])
    trial = expts[trial_number]
    trial_curves = trial.lightcurves
    for reference_curveI in range(len(reference_events)):
        reference_batch = reference_events[reference_curveI]
        reference_batch.curve_id = reference_curveI
        reference_slices = list(map(lambda x: x.slice_object,reference_batch))
        curr_radius_line = trial_curves[reference_curveI]
        curr_radius_line.curve_id = reference_curveI
        curr_radius_line.trial_id = trial_number
        events_in_r = curr_radius_line.get_slices(reference_slices)
        batch_for_radius = batch_for_radius + events_in_r
        batch_for_radius.trial_id = trial_number
    list_of_events[trial_number] = batch_for_radius
#So each element of list_of_events is a LightCurveBatch, with all the events
#At the radius indicated by the index of the element in list_of_events,
#In the same order
for group in reference_events:
    all_ref_batch = all_ref_batch + group
table = LightCurveClassificationTable(all_ref_batch,1e-10,method='Prominence')
grouped_by_event = []
double_horns = table[0]
trials = list(map(lambda t:t.lightcurves,expts))
print("In Double Horns")
for sliced_event in double_horns:
    all_radii_of_event = []
    curve_id = sliced_event.parent_curve.curve_id
    slice_obj = sliced_event.slice_object
    for i in range(0,20):
        lightcurves = trials[i]
        curve = lightcurves[curve_id]
        curve.curve_id = curve_id
        sliced = curve[slice_obj]
        all_radii_of_event.append(sliced)
    grouped_by_event.append(all_radii_of_event)
import pickle
def save_pickled(fname,obj):
    with open(fname,'wb+') as f:
        pickle.dump(obj,f)
shift_array = np.ndarray((len(grouped_by_event),20))
from mirage.light_curves.peak_finding import prominences
def argTopTwoPeaks(curve):
    possible, = argrelmax(curve)
    if len(possible) == 0:
        return [np.nan,np.nan]
    elif len(possible) == 1:
        return [possible[0],np.nan]
    else:
        proms = prominences(curve,possible)
        top_two = np.argpartition(proms,len(proms) - 1)[-2:]
        return [possible[top_two[0]],possible[top_two[1]]]
print("Grouping")
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        shift_array[eventI,radiusI] = first_peak - first_corr
print("Describing")
from scipy.stats import describe
abs_arr = abs(shift_array)
stats = describe(abs_arr,nan_policy='omit')
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
for i in range(len(curves)):
    curve = curves[i]
    curve.curve_id = i
    events = curve.get_events(2,151,u.Quantity(9,'uas'),u.Quantity(4,'uas'),10)
    events = list(map(lambda x: x,events))
    slices = list(map(lambda x: x.slice_object,events))
    unfiltered = curve_course[i].get_slices(slices)
    unfiltered.curve_id = i
    reference_events.append(events)
#Now construct a list of LightCurveBatches,
#Where each element represents a different quasar radius
#And each LightCurveBatch contains all the events for that radius.
list_of_events = [None]*20
print("Second for loop")
for trial_number in range(20):
    batch_for_radius = LightCurveBatch([])
    trial = expts[trial_number]
    trial_curves = trial.lightcurves
    for reference_curveI in range(len(reference_events)):
        reference_batch = reference_events[reference_curveI]
        reference_batch.curve_id = reference_curveI
        reference_slices = list(map(lambda x: x.slice_object,reference_batch))
        curr_radius_line = trial_curves[reference_curveI]
        curr_radius_line.curve_id = reference_curveI
        curr_radius_line.trial_id = trial_number
        events_in_r = curr_radius_line.get_slices(reference_slices)
        batch_for_radius = batch_for_radius + events_in_r
        batch_for_radius.trial_id = trial_number
    list_of_events[trial_number] = batch_for_radius
#So each element of list_of_events is a LightCurveBatch, with all the events
#At the radius indicated by the index of the element in list_of_events,
#In the same order
for group in reference_events:
    all_ref_batch = all_ref_batch + group
table = LightCurveClassificationTable(all_ref_batch,1e-10,method='Prominence')
grouped_by_event = []
double_horns = table[0]
trials = list(map(lambda t:t.lightcurves,expts))
print("In Double Horns")
for sliced_event in double_horns:
    all_radii_of_event = []
    curve_id = sliced_event.parent_curve.curve_id
    slice_obj = sliced_event.slice_object
    for i in range(0,20):
        lightcurves = trials[i]
        curve = lightcurves[curve_id]
        curve.curve_id = curve_id
        sliced = curve[slice_obj]
        all_radii_of_event.append(sliced)
    grouped_by_event.append(all_radii_of_event)
import pickle
def save_pickled(fname,obj):
    with open(fname,'wb+') as f:
        pickle.dump(obj,f)
shift_array = np.ndarray((len(grouped_by_event),20))
from mirage.light_curves.peak_finding import prominences
def argTopTwoPeaks(curve):
    possible, = argrelmax(curve)
    if len(possible) == 0:
        return [np.nan,np.nan]
    elif len(possible) == 1:
        return [possible[0],np.nan]
    else:
        proms = prominences(curve,possible)
        top_two = np.argpartition(proms,len(proms) - 1)[-2:]
        return [possible[top_two[0]],possible[top_two[1]]]
print("Grouping")
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        shift_array[eventI,radiusI] = first_peak - first_corr
print("Describing")
from scipy.stats import describe
abs_arr = abs(shift_array)
stats = describe(abs_arr,nan_policy='omit')
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
for i in range(len(curves)):
    curve = curves[i]
    curve.curve_id = i
    events = curve.get_events(2,151,u.Quantity(9,'uas'),u.Quantity(4,'uas'),10)
    # events = list(map(lambda x: x,events))
    slices = list(map(lambda x: x.slice_object,events))
    unfiltered = curve_course[i].get_slices(slices)
    unfiltered.curve_id = i
    reference_events.append(events)
#Now construct a list of LightCurveBatches,
#Where each element represents a different quasar radius
#And each LightCurveBatch contains all the events for that radius.
list_of_events = [None]*20
print("Second for loop")
for trial_number in range(20):
    batch_for_radius = LightCurveBatch([])
    trial = expts[trial_number]
    trial_curves = trial.lightcurves
    for reference_curveI in range(len(reference_events)):
        reference_batch = reference_events[reference_curveI]
        reference_batch.curve_id = reference_curveI
        reference_slices = list(map(lambda x: x.slice_object,reference_batch))
        curr_radius_line = trial_curves[reference_curveI]
        curr_radius_line.curve_id = reference_curveI
        curr_radius_line.trial_id = trial_number
        events_in_r = curr_radius_line.get_slices(reference_slices)
        batch_for_radius = batch_for_radius + events_in_r
        batch_for_radius.trial_id = trial_number
    list_of_events[trial_number] = batch_for_radius
#So each element of list_of_events is a LightCurveBatch, with all the events
#At the radius indicated by the index of the element in list_of_events,
#In the same order
for group in reference_events:
    all_ref_batch = all_ref_batch + group
table = LightCurveClassificationTable(all_ref_batch,1e-10,method='Prominence')
grouped_by_event = []
double_horns = table[0]
trials = list(map(lambda t:t.lightcurves,expts))
print("In Double Horns")
for sliced_event in double_horns:
    all_radii_of_event = []
    curve_id = sliced_event.parent_curve.curve_id
    slice_obj = sliced_event.slice_object
    for i in range(0,20):
        lightcurves = trials[i]
        curve = lightcurves[curve_id]
        curve.curve_id = curve_id
        sliced = curve[slice_obj]
        all_radii_of_event.append(sliced)
    grouped_by_event.append(all_radii_of_event)
import pickle
def save_pickled(fname,obj):
    with open(fname,'wb+') as f:
        pickle.dump(obj,f)
shift_array = np.ndarray((len(grouped_by_event),20))
from mirage.light_curves.peak_finding import prominences
def argTopTwoPeaks(curve):
    possible, = argrelmax(curve)
    if len(possible) == 0:
        return [np.nan,np.nan]
    elif len(possible) == 1:
        return [possible[0],np.nan]
    else:
        proms = prominences(curve,possible)
        top_two = np.argpartition(proms,len(proms) - 1)[-2:]
        return [possible[top_two[0]],possible[top_two[1]]]
print("Grouping")
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        shift_array[eventI,radiusI] = first_peak - first_corr
print("Describing")
from scipy.stats import describe
abs_arr = abs(shift_array)
stats = describe(abs_arr,nan_policy='omit')
stats
plt.plot(stats.mean)
plt.plot(stats.mean,'.')
grouped_by_event[0]
for e in grouped_by_event[0]: plt.plot(*e.plottable_segment())
np.histogram
grouped_by_radius = []*20
grouped_by_radius
grouped_by_radius = [None]*20
grouped_by_radius
grouped_by_radius = [[]]*20
grouped_by_radius
shift_array.shape
r1 = shift_array[:,0]
np.histogram
r1.shape
def hist(data,n):
    ret = np.histogram(data,n+1)
    c = ret[0]
    b = ret[1][1:]
    plt.plot(c,b)
    
hist(r1,100)
def hist(data,n):
    ret = np.histogram(data,n+1)
    c = ret[0]
    b = ret[1][1:]
    plt.plot(b,c)
    
hist(r1,100)
def hist(data,n):
    ret = np.histogram(data,n+1)
    c = ret[0]
    b = ret[1][1:]
    plt.bar(b,c)
    
hist(r1,100)
r2 = shift_array[:,1]
hist(r2,100)
import pandas as pd
pd.DataFrame
df = pd.DataFrame(shift_array,columns = ['shift','rad'])
shift_array.shape
tmp = []
radii = np.linspace(5,40,20)
for i in range(shift_array.shape[0]):
    for j in range(shift_array.shape[1]):
        tmp.append([shift_array[i,j],radii[j]])
tmpdf = pd.DataFrame(tmp,columns=['radius','curve'],dtype=object)
tmp = []
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        tmp.append([radii[radiusI],grouped_by_event[eventI][radiusI]])
tmpdf = pd.DataFrame(tmp,columns=['radius','curve'])
tmpdf['length'] = tmpdf['curve'].apply(lambda x: x.length.to('uas').value)
master_df = pd.merge(df,tmpdf,on='index')
tmp = []
for eventI in range(len(grouped_by_event)):
    ref_peaks = argTopTwoPeaks(grouped_by_event[eventI][0].curve)
    first_peak = min(ref_peaks)
    second_peak = max(ref_peaks)
    for radiusI in range(20):
        corresponding_slice = grouped_by_event[eventI][radiusI]
        corr_peaks = argTopTwoPeaks(corresponding_slice.curve)
        first_corr = min(corr_peaks)
        second_corr = max(corr_peaks)
        #Only looking at the first peak
        tmp.append([eventI*20+radiusI,radii[radiusI],grouped_by_event[eventI][radiusI]])
tmpdf = pd.DataFrame(tmp,columns=['id','radius','curve'])
tmpdf['length'] = tmpdf['curve'].apply(lambda x: x.length.to('uas').value)
tmp = []
for i in range(shift_array.shape[0]):
    for j in range(shift_array.shape[1]):
        tmp.append([i*20+j,shift_array[i,j],radii[j]])
df = pd.DataFrame(tmp,columns = ['id','shift','rad'])
df['abs_dif'] = abs(df['shift'])
master_df = pd.merge(df,tmpdf,on='id')
master_df['plottable'] = master_df['curve'].apply(lambda x: x.curve)
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
master_df['peaks'] = master_df['plottable'].apply(lambda x: get_exact_peaks(x,2,50))
master_df['p1'] = master_df['peaks'].apply(lambda x: min(x))
master_df['p2'] = master_df['peaks'].apply(lambda x: max(x))
d1 = master_df.copy()
d2 = master_df.copy()
d2['d1'] = d2['d2']
total = d2.append(d1)
master_df= total.copy()
