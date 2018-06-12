import numpy as np
from scipy import optimize
from scipy import interpolate
from matplotlib import pyplot as pl

def getPeaksOf(y,num_peaks,x_threshold):
    indices = np.argpartition(y,len(y) - num_peaks)[-num_peaks:]
    indices = np.sort(indices)
    trimmed = []
    trimmed.append(indices[0])
    for i in indices:
        if i - trimmed[-1] < x_threshold:
            if y[trimmed[-1]] > y[i]: pass
            else: trimmed[-1] = i
        else: trimmed.append(i)
    return np.array(trimmed)

def findCorrespondingPeaks(peaks1,x,y,window=3):
    peaks2 = np.zeros_like(peaks1)
    for i in range(len(peaks1)):
        ind = peaks1[i]
        a = max(ind-window,0)
        b = min(ind+window,len(y)-1)
        s = interpolate.UnivariateSpline(x,-y)
        s.set_smoothing_factor(0)
        maxx = optimize.brent(s,brack=(x[a],x[b]))
        peaks2[i] = np.searchsorted(x,[maxx])
    return peaks2

def plot_maxes(xx,yy,inds):
    for ind in inds:
        x = xx[ind]
        y = yy[ind]
        if plotting:
            plt.plot(x,y,'+',markersize=20.0)

def get_all(curves,num_peaks,r_ratio,engine,radius,plotting = True):
    counter = 1
    ret = []
    for curve in curves:
        ret.append(getDiffs(curve,num_peaks,radius,engine,r_ratio,plotting))
        if plotting:
            plt.title('Curve' + str(counter))
        counter += 1
    return ret

def getDiffs(curve,num_peaks,radius,engine,r_ratio,with_plotting = True):
    x,y1 = curve.plottable('uas')
    xv = x.value
    qpts = curve.query_points
    y2 = eng.query_line(qpts,radius*r_ratio)
    x_threshold = int(3/(xv[1]-xv[0]))
    peaks1 = getPeaksOf(y1,num_peaks,x_threshold)
    peaks2 = findCorrespondingPeaks(peaks1,xv,y2)
    if with_plotting:
        plt.figure()
        plt.plot(x,y1)
        plt.plot(x,y2)
        plot_maxes(xv,y1,peaks1)
        plot_maxes(xv,y2,peaks2)
    diffs = np.ones_like(peaks1,dtype=float)
    for i in range(len(peaks1)):
        diffs[i] = xv[peaks1[i]] - xv[peaks2[i]]
    return diffs