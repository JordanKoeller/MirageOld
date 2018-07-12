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
help(pd.DataFrame)
df = pd.DataFrame(shift_array,columns = ['shift','rad'])
shift_array.shape
for i in range(shift_array.shape[0]):
    for j in range(shift_array.shape[1]):
        tmp.append([shift_array[i,j],radii[j]])
        
        
        
        
tmp = []
radii = np.linspace(5,40,20)
for i in range(shift_array.shape[0]):
    for j in range(shift_array.shape[1]):
        tmp.append([shift_array[i,j],radii[j]])
        
        
        
        
tmp = np.array(tmp)
df = pd.DataFrame(tmp,columns = ['shift','rad'])
df
df['abs_dif'] = abs(df['shift'])
df.hist('abs_dif',by='radius')
df.hist('abs_dif',by='rad',bins=100)
df.hist('abs_dif',by='rad',bins=300,sharex=True)
df.hist('abs_dif',by='rad',bins=300,sharex=True,sharey=True)
fil = df[df['abs_dif'] < 200]
d = fil.describe()
d
grouped = d.groupby('rad')
d = grouped.describe()
d
d['mean']
d
d['mean']
d
d['abs_dif']
d['abs_dif']['mean']
plt.plot(d['abs_dif']['mean'])
plt.plot(d['abs_dif']['mean'],'.')
plt.plot(d['abs_dif']['mean'][:-1],'.')
plt.plot(d['abs_dif']['mean'],'.')
df
df['rad'].unique()
fil = df[df['abs_dif'] < 200]
fil['rad'].unique()
grouped = d.groupby('rad')
len(grouped)
grouped = fil.groupby('rad')
d = grouped.describe()
plt.plot(d['abs_dif']['mean'],'.')
d['abs_dif']['std']
plt.errorbar(x = np.arange(5,20,40),d['abs_dif']['mean']*0.01,yerr=d['abs_dif']['std'])
plt.errorbar(x = np.arange(5,20,40),y=d['abs_dif']['mean']*0.01,yerr=d['abs_dif']['std'])
d['abs_dif']['mean']
d['abs_dif']['std']
x = np.arange(5,40,20)
plt.errorbar(x,d['abs_dif']['mean'],yerr=d['abs_dif']['std'])
d['abs_dif']['std']
d['abs_dif']['std'].shape
mean = d['abs_dif']['mean']
std = d['abs_dif']['std']
mean.shape
std.shape
x
x.shape
x = np.linspace(5,40,20)
plt.plot(x,mean,yerr=std)
plt.errorbar(x,mean,yerr=std)
plt.errorbar(x,mean,yerr=std,fmt='.')
def gen():
    for event in grouped_by_event:
        for line in event:
            plt.plot(event.curve)
        yield
        
g = gen()
next(g)
grouped_by_event[0]
grouped_by_event[0][0]
def gen():
    for event in grouped_by_event:
        for line in event:
            plt.plot(line.curve)
        yield
        
g = gen()
next(g)
def gen():
    for event in grouped_by_event:
        for line in event:
            plt.plot(line.curve)
        yield
        plt.close()
        
g = gen()
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
next(g)
g = gen()
g = gen()
next(g)
next(g)
next(g)
next(g)
next(g)
expts
la.visualizeMagMap(expts[0])
la.visualizeMagMap(expts[1])
la.visualizeMagMap(expts[5])
la.visualizeMagMap(expts[10])
la.visualizeMagMap(expts[15])
la.visualizeMagMap(expts[19])
la.visualizeMagMap(expts[20])
table
t1 = table[0]
t1
plt.plot(*t1[0].plottable())
plt.plot(*t1[1].plottable())
plt.plot(*t1[2].plottable())
plt.plot(*t1[3].plottable())
plt.plot(*t1[4].plottable())
plt.plot(*t1[5].plottable())
plt.plot(*t1[6].plottable())
plt.plot(*t1[7].plottable())
plt.plot(*t1[8].plottable())
plt.plot(*t1[9].plottable())
plt.plot(*t1[10].plottable())
plt.plot(*t1[11].plottable())
tmp
len(grouped_by_event)
trials
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
        
tmp
tmpdf = pd.DataFrame(tmp,columns=['radius','curve'])
tmpdf
tmpdf[0]
tmp[0]
tmpdf = pd.DataFrame(tmp,columns=['radius','curve'],dtype=object)
tmpdf
tmpdf.dtypes
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
        tmp.append([radii[radiusI],[grouped_by_event[eventI][radiusI]]])
        
tmpdf = pd.DataFrame(tmp,columns=['radius','curve'],dtype=object)
tmpdf
tmpdf['curve']
tmpdf.ati
tmpdf['curve'].iloc(0)
tmpdf['curve'].iloc(0)[0]
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
tmpdf['curve'].iloc(0)[0]
tmpdf['curve']
tmpdf['curve'].apply
help(tmpdf['curve'].apply)
tmpdf['length'] = tmpdf['curve'].apply(lambda x: x.length)
tmpdf
tmpdf['length'] = tmpdf['curve'].apply(lambda x: x.length.value)
tmpdf['length'] = tmpdf['curve'].apply(lambda x: x.length.to('uas').value)
tmpdf
master_df = pd.merge(df,tmpdf,on='index')
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
df
tmp = []
for i in range(shift_array.shape[0]):
    for j in range(shift_array.shape[1]):
        tmp.append([i*20+j,shift_array[i,j],radii[j]])
        
        
        
        
df = pd.DataFrame(tmp,columns = ['id','shift','rad'])
df['abs_dif'] = abs(df['shift'])
master_df = pd.merge(df,tmpdf,on='id')
master_df
len(master_df)
len(df)
len(tmpdf)
e1 = master_df.iloc(0,20)
e1 = master_df.iloc(0:20)
e1 = master_df.iloc(slice(0,20))
e1 = master_df.iloc[slice(0,20)]
e1
master_df['plottable'] = master_df['curve'].apply(lambda x: x.curve)
e1 = master_df.iloc[slice(0,20)]
e1
plt.plot(e1['plottable'])
master_df.foreach
e1['curve'].apply(lambda x: plt.plot(*x.plottable()))
master_df.iloc[0].apply
master_df.iloc[0].apply(lambda x: x['rad'])
master_df.iloc[0].apply(lambda x: print(x))
master_df.iloc[0].apply(lambda x: print(type(x)))
master_df.iloc[0].apply(lambda x: print(class(x)))
long_enough = master_df[master_df['length'] > 1.0]
long_enough.hist('abs_dif',by='rad',bins=300,sharex=True,sharey=True)
master_df['length']
def gen():
    for i in range(100):
        tmp = long_enough.iloc[i*20:i*20+20]
        tmp['plottable'].apply(lambda x: plt.plot(x))
        print(tmp['abs_dif'])
        yield
        plt.close()
        
g = gen()
next(g)
def applicator(plotter):
    plt.figure()
    plt.plot(plotter,label=str(c))
    plt.title(str(c))
    c += 1
    
def gen():
    for i in range(100):
        tmp = long_enough.iloc[i*20:i*20+20]
        tmp['plottable'].apply(applicator)
        print(tmp['abs_dif'])
        yield
        plt.close()
        
c = 0
g = gen()
next(g)
c = 0
g = gen()
next(g)
def applicator(plotter):
    plt.figure()
    plt.plot(plotter)
    
    
g = gen()
next(g)
master_df
next(g)
def applicator(plotter):
    plt.plot(plotter)
    
    
g = gen()
next(g)
next(g)
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
master_df['peaks'] = masater_df['plottable'].apply(lambda x: get_exact_peaks(x,2,200)
)
master_df['peaks'] = master_df['plottable'].apply(lambda x: get_exact_peaks(x,2,200))
r1 = master_df.iloc[0]
r1
r1['id']
plt.plot(r1['plottable'])
master_df['peaks'] = master_df['plottable'].apply(lambda x: get_exact_peaks(x,2,50))
r1 = master_df.iloc[0]
plt.plot(r1['plottable'])
peaks = r1['peaks']
peaks[0]
peaks[1]
plt.plot(np.arange(0,20)*0+8,np.arange(0,20))
plt.plot(np.arange(0,20)*0+122,np.arange(0,20))
master_df['p1'] = master_df['peaks'].apply(lambda x: min(x))
master_df['p2'] = master_df['peaks'].apply(lambda x: max(x))
def gen():
    for i in range(100):
        tmp = long_enough.iloc[i*20:i*20+20]
        tmp['plottable'].apply(applicator)
        print(tmp['abs_dif'])
        yield
        plt.close()
        
g = gen()
next(g)
references = master_df[master_df['rad'] == 5.0]
references
def get_shift(row):
    p = row['p1']
    ref = references[row['id'] // 20]
    return abs(p - ref)
master_df['d1'] = master_df.apply(get_shift)
master_df['d1'] = master_df.apply(axis=1,get_shift)
master_df['d1'] = master_df.apply(get_shift,axis=1)
def get_shift(row):
    p = row['p1']
    ref = references['p1'].iloc[row['id'] // 20]
    return abs(p - ref)
references['p1'].iloc[0]
master_df['d1'] = master_df.apply(get_shift,axis=1)
def get_shift(row):
    p = row['p2']
    ref = references['p2'].iloc[row['id'] // 20]
    return abs(p - ref)
master_df['d2'] = master_df.apply(get_shift,axis=1)
master_df.hist('d1',by='rad',bins=300,sharex=True,sharey=True)
grouped = master_df.describe()
grouped = master_df.groupby('rad').describe()
groupe
grouped
grouped['d1']
grouped['d1']
grouped['d2']
grouped['d1']
def check_plot(row_id):
    plt.figure()
    plt.plot(master_df.iloc[row_id]['plottable'])
    plt.plot(master_df.iloc[row_id // 20]['plottable'])
    
extremes = master_df[master_df['d1'] > 100]
extremes
extremes['id'].iloc[0:10].apply(check_plot)
extremes['id'].iloc[0:10].apply(lambda x: print(x))
def gen():
    for i in range(1180):
        tmp = long_enough.iloc[i*20:i*20+20]
        tmp['plottable'].apply(applicator)
        print(tmp['abs_dif'])
        yield
        plt.close()
        
g = gen()
plt.figure()
next(g)
def gen():
    for i in range(1180,1220):
        tmp = long_enough.iloc[i*20:i*20+20]
        tmp['plottable'].apply(applicator)
        print(tmp['abs_dif'])
        yield
        plt.close()
        
g = gen()
plt.figure()
next(g)
def gen():
    for i in range(1180,1200):
        tmp = long_enough.iloc[i*20:i*20+20]
        master_df['plottable'].apply(applicator)
        print(master_df['d1'])
        yield
        plt.close()
        
        
g = gen()
next(g)
def gen():
    for i in range(1180,1200):
        tmp = master_df.iloc[i]
        tmp['plottable'].apply(applicator)
        print(tmp['d1'])
        yield
        plt.close()
        
        
g = gen()
next(g)
def gen():
    for i in range(1180,1200):
        tmp = master_df.iloc[i]
        plt.plot(tmp['plottable'])
        print(tmp['d1'])
        yield
        plt.close()
        
        
g = gen()
next(g)
plt.figure()
g = gen()
n
next(g)
next(g)
def gen():
    for i in range(1180,1200):
        tmp = master_df.iloc[i]
        plt.plot(tmp['plottable'])
        print(tmp['d1'])
        
        
        
plt.figure()
gen()
e1 = master_df.iloc[1180:1200]
e1
plt.figure()
e1['plottable'].apply(plt.plot)
def show_peaks(row):
    p1,p2 = row['p1'],row['p2']
    y1 = row['plottable'][p1]
    y2 = row['plottable'][p2]
    plt.plot(p1,y1,'+')
    plt.plot(p2,y2,'+')
    
e1.apply(show_peaks,axis=1)
long_enough = master_df[master_df['length'] > 200]
long_enough = master_df[(master_df['length'] > 200) & ((master_df['d1'] < 100]) & ( master_df['d2'] < 100]))]
long_enough = master_df[(master_df['length'] > 200) & (master_df['d1'] < 100]) & ( master_df['d2'] < 100])]
long_enough = master_df[(master_df['length'] > 200) & (master_df['d1'] < 100]) & (master_df['d2'] < 100)]
long_enough = master_df[(master_df['length'] > 200) & (master_df['d1'] < 100]) & (master_df['d2'] < 100)]
long_enough = master_df[(master_df['length'] > 200) & (master_df['d1'] < 100) & (master_df['d2'] < 100)]
long_enough.hist('d1',by='rad',bins=300,sharex=True,sharey=True)
long_enough
long_enough = master_df[(master_df['length'] > 2) & (master_df['d1'] < 100) & (master_df['d2'] < 100)]
long_enough
long_enough.hist('d1',by='rad',bins=300,sharex=True,sharey=True)
d1 = master_df.copy()
d2 = master_df.copy()
d1['d1'] - d1['d1']
d2['d1'] = d2['d2']
total = d2.append(d1)
total
total.hist('d1',by='rad',bins=300,sharex=True,sharey=True)
stats = total.groupby('rad').describe()
stats['d1']
total.percentile
stats = total.groupby('rad').describe(percentiles=['0.5','0.75','0.9','0.95'])
stats = total.groupby('rad').describe(percentiles=[0.5,0.75,0.9,0.95])
stats['d1']
master_df= total.copy()
filtered = total[total['d1'] < 50]
stats = total.groupby('rad').describe(percentiles=[0.5,0.75,0.9,0.95,99])
stats = total.groupby('rad').describe(percentiles=[0.5,0.75,0.9,0.95,0.99])
stats['d1']
filtered = total[total['d1'] < 100]
filtered.hist('d1',by='rad',bins=100,sharex=True,sharey=True)
filtered.hist('d1',by='rad',bins=50,sharex=True,sharey=True)
stats = filtered.groupby('rad').describe(percentiles=[0.5,0.75,0.9,0.95,0.99])
stats['d1']
master_df['d1'] = master_df['df']*0.01
master_df['d1'] = master_df['d1']*0.01
filtered['d1'] = filtered['d1']*0.01
master_df['d1']
filtered
filtered.hist('d1',by='rad',bins=50,sharex=True,sharey=True)
stats = filtered.groupby('rad').describe(percentiles=[0.5,0.75,0.9,0.95,0.99])
plt.errorbar(np.linspace(5,40,20),stats['d1']['mean'],yerr=stats['d1']['std'])
plt.errorbar(np.linspace(5,40,20),stats['d1']['mean'],yerr=stats['d1']['std'],fmt='.')
stats['d1']['std']
