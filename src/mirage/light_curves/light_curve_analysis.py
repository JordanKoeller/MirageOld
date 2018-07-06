import numpy as np
from scipy.stats import sigmaclip
from scipy.signal import savgol_filter, wiener
from scipy.interpolate import UnivariateSpline
from numpy import percentile


def determine_baseline(y,sigma=3):
    """Function for determining the approximate baseline value of the light curve through sigma clipping.
    Arguments:
        y {:class:`np.ndarray`} -- The light curve to inspect. Should be a one-dimensional array.

    Returns:
        A tuple of (baseline, approximate noise) as :class:`(float,float)`
    """
    clipped = sigmaclip(y,sigma,sigma)
    mean = clipped.clipped.mean()
    noise = (clipped.upper+clipped.lower)/2
    return (mean,noise)


def get_peaks_above(y,y_threshold,x_separation):
    """Tabulates and returns the indices of peaks in a light curve above a certain value.
    
    This algorithm scans through a light curve and pulls out the indices where the light curve peaks above a certain value.
    It returns one index per peak, which is determined by the `x_separation` parameter, which describes how dense you expect the peaks
    to be. It will not return two peaks within an `x_separation` distance of each other.
    
    Arguments:
        y {:class:`np.ndarray`} -- The y-values for the light curve to analyze. Should be a one-dimensional array
        y_threshold {:class:`float`} -- The y-value that the peak must exceed for it to be recorded.
        x_separation {`int`} -- The minimum distance two peaks must be separated by. The separation is measured in indices. For example,
        if `x_separation` is specified as 7, and the algorithm finds a peak at index `12`, It cannot return any more peaks within the range 
        of indices (12-7) to (12+7). If another peak is found within this window, it chooses the taller of the two peaks.
    
    Returns:
        `np.ndarray` -- An array of the index positions of the discovered peaks.
    """
    indices = np.argsort(y)[::-1]
    trimmed = []
    trimmed.append(indices[0])
    i = 1
    f1 = True
    while f1 and i < len(y):
        flag = True
        for peak in trimmed:
            if abs(peak - indices[i]) < x_separation:
                flag = False
        if flag:
            if y[indices[i]] > y_threshold:
                trimmed.append(indices[i])
            else:
                f1 = False
        i += 1
    return np.array(trimmed)


def slice_peak(y,peak_index,baseline,noise,trim_tails=False):
    """function for isolating a microlensing event in a light curve.
    
    Given a peak to isolate, this function returns an array, which is a slice of the light curve that defines the peak.
    It does this by expanding around the peak, searching for when it has returned to baseline for an adequately long time.
    
    Arguments:
        y {`np.ndarray`} -- The light curve to slice. Should be a 1D array.
        peak_index {`int`} -- The index of the peak to isolate in the light curve
        baseline {`float`} -- The y-value of the light curve representing the baseline value.
        noise {`float`} -- A parameter to describe how noisy the data is. In other words, the amount by which the light curve fluctuates
        around the baseline away from any microlensing event.

    Keyword Arguments:
        trim_tails {`bool`} -- If set to true, the algorithm will trim any parts of the slices that are near horizontal, such that the
        peak returned is only the section where the light curve is actively rising and falling. (Default: `False`)
    
    Returns:
        `np.ndarray` -- The slice of `y` that describes the peak.
    """
    thresh = baseline + noise
    min_scanner = peak_index
    max_scanner = peak_index
    flag1 = True
    flag2 = True
    while flag1 or flag2:
        if y[min_scanner] > thresh:
            min_scanner -= 1
        else:
            flag1 = False
        if y[max_scanner] > thresh:
            max_scanner += 1
        else:
            flag2 = False
    if trim_tails:
        avg_window = 7 #May want to pass this in.
        slope = (y[min_scanner+avg_window]-y[min_scanner])/7
        while slope < 0.5 and min_scanner < peak_index:
            min_scanner += int(avg_window*2/3)
            slope = (y[min_scanner+avg_window]-y[min_scanner])/7
        slope = (y[max_scanner]-y[max_scanner-avg_window])/7
        while slope > -0.5 and max_scanner > peak_index:
            max_scanner -= int(avg_window*2/3)
            slope = (y[max_scanner]-y[max_scanner-avg_window])/7
    sliced = y[min_scanner:max_scanner]
    return sliced



def fit_peak(sliced_peak,order=4):
    """Calculates and returns the coefficients of a polynomial that best fit the peak.
    
    This algorithm uses a least-squares fit to fit the passed in light curve peak to a polynomial of degree `order`.
    
    Arguments:
        sliced_peak {`np.ndarray`} -- A 1D numpy array, containing the y-values of the peak in interest
    
    Keyword Arguments:
        order {`int`} -- The order of polynomial to fit the light curve to. (default: {4})

    Returns:
        (coefficients,r2) {(`np.ndarray`,`float`)} -- The coefficients dsicovered that fit the peak best, as well as the r^2 value of the fit.
        The coefficieints array will be of shape (`order`,)
    """
    x_array = np.arange(len(sliced_peak),dtype=float)/len(sliced_peak)
    internal = sliced_peak.copy()
    internal -= internal[0]
    coeffs = np.polyfit(x_array,internal,order)
    return coeffs

def build_estimate(x,coeffs):
    y = np.ones_like(x,dtype=float)-1.0
    for i in range(len(coeffs)):
        y += coeffs[i]*x**(len(coeffs)-1-i)
    return y


def get_all_coefficients(line,x_threshold,y_threshold,with_plotting = True):
    peaks = get_peaks_above(line,y_threshold,x_threshold)
    print(len(peaks))
    baseline, noise = determine_baseline(line)
    print("Baseline, noise" + str(baseline) + "," + str(noise))
    tmp = []
    for peak in peaks:
        try:
            print("Doing peak" + str(peak))
            # plt.figure()
            peak_slice = slice_peak(line,peak,baseline,noise,True)
            coeffs = fit_peak(peak_slice,4)
            tmp.append(coeffs)
            plt.plot(peak_slice)
            est = build_estimate(np.arange(len(peak_slice)),coeffs)
            plt.plot(est)
        except:
            print("Failed on peak" + str(peak) + ". Excluding")
    return tmp


def isolate_events(line,tolerance,sigma,smoothing_window=55,tail_factor=0.1):
    # baseline, noise = determine_baseline(line)
    x = np.arange(len(line))
    spline = UnivariateSpline(x,line)
    spline.set_smoothing_factor(0)
    spline_deriv = spline.derivative()
    smooth_deriv_abs = wiener(abs(spline_deriv(x)),smoothing_window)
    deriv_baseline, deriv_noise = determine_baseline(smooth_deriv_abs,sigma)
    deriv_threshold = deriv_baseline+deriv_noise
    # plt.plot(smooth_deriv_abs)
    # plt.plot(smooth_deriv_abs*0+deriv_threshold)
    # plt.show()
    cross_point_groups = []
    i = 0
    while i < len(smooth_deriv_abs)-1:
        if smooth_deriv_abs[i] < deriv_threshold and smooth_deriv_abs[i+1] >= deriv_threshold:
            # print("Found first upper")
            cross_up = i+1
            i += 1
            while i < len(smooth_deriv_abs) and smooth_deriv_abs[i] > deriv_threshold: i += 1
            cross_down = i-1
            cross_point_groups.append([cross_up,cross_down])
        else:
            i += 1
    line_threshold = line.mean()+tolerance
    events = []
    cross_I = 0
    while cross_I < len(cross_point_groups):
        if line[cross_point_groups[cross_I][0]] < line_threshold:
            event_start = cross_point_groups[cross_I][0]
            event_end = None
            #use a while True: if flag: break to emulate a do while loop
            while True:
                event_end = cross_point_groups[cross_I][1]
                if line[event_end] < line_threshold: 
                    break
                else:
                    cross_I += 1
            if event_end - event_start > 0 and line[event_start:event_end].max() > line_threshold:
                center = (event_start+event_end)/2
                split = (event_end - event_start)/2
                scaled = split*(1+tail_factor)
                event_start = max(0,int(center - scaled))
                event_end = min(len(line)-1,int(center+scaled))
                events.append([event_start,event_end])
        cross_I += 1
    event_slices = list(map(lambda event: line[event[0]:event[1]], events))
    return (events,event_slices)

    
def categorize_curves(curves,p_threshold,method,*args,**kwargs):
    #cramer von-mises is the way to go. Callable with 
    #scipy.stats.energy_distance
    table = []
    table.append([curves[0]])
    for curveI in range(1,len(curves)):
        curve = curves[curveI]
        if len(curve) < 100:
            continue
        most_similar = -1
        best_p = 1000
        for i in range(len(table)):
            row = table[i]
            rep = row[0]
            d,p_val = method(curve,rep,*args,**kwargs)
            if p_val < p_threshold:
                found_match = True
                if p_val < best_p:
                    best_p = p_val
                    most_similar = i
        if most_similar == -1:
            table.append([curve])
        else:
            table[most_similar].append(curve)
    return table

def describe_table(table):
    for i in range(len(table)):
        print("Index " + str(i) + " of length " + str(len(table[i])))

