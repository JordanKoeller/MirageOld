import numpy as np
from scipy.signal import savgol_filter



def determine_baseline(y):
	"""Function for determining the approximate baseline value of the light curve.
	
	This function is built on the assumption that the magnification coefficient spends most of its time around baseline.
	By taking advantage of this property, it calculates the mode of the line, and then based on the distribution of values
	near the baseline, deterimes an estimate of typical deviation from the baseline caused by noise.
	
	Arguments:
		y {:class:`np.ndarray`} -- The light curve to inspect. Should be a one-dimensional array.

	Returns:
		A tuple of (baseline, approximate noise) as :class:`(float,float)`
	"""
	hist, bins = np.hist(y,bins=200,density=True)
	peak_ind = np.argmax(hist)
	mode = bins[peak_ind]
	scanner = peak_ind
	while hist[scanner] > 0.05: scanner += 1
	noise = bins[scanner]
	return (mode,noise-mode)


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
