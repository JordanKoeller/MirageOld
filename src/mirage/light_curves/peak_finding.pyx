# cython: cdivision=True
# cython: wraparound=False
# cython: boundscheck=False

import numpy as np
cimport numpy as np
from scipy.stats import sigmaclip
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from scipy.ndimage.filters import gaussian_filter
from libc.math cimport sqrt 

cdef determine_baseline(np.ndarray[np.float64_t,ndim=1] y,double sigma=3.0):
    clipped = sigmaclip(y,sigma,sigma)
    mean = clipped.clipped.mean()
    noise = (clipped.upper + clipped.lower)/2.0
    return (mean, noise)

cpdef isolate_events(np.ndarray[np.float64_t, ndim=1] line, double tolerance=1.0, int smoothing_window=55,int max_length=-1):
#NEW IDEA: Use maximizing summed curvature as a heuristic for when an event has occurred?
    cdef:
        np.ndarray[np.float64_t, ndim=1] x = np.arange(len(line),dtype=np.float64)
        np.ndarray[np.float64_t, ndim=1] threshold_line = gaussian_filter(line,len(line)*3/smoothing_window)
        double deriv_baseline, deriv_noise, deriv_threshold, center, split, scaled, slice_max, slice_min
        int i, cross_I, cross_up, cross_down, event_end, event_start, line_length, num_groups, line_length2, k
        vector[pair[int,int]] cross_point_groups, events, events2
        pair[int,int] group1, group2, group3
        int w1, w2, w3
    line_length = len(line) - 1 
    line_length2 = len(line)
    i = 0
    with nogil:
        while i < line_length - 1:
            if line[i] < threshold_line[i] and line[i+1] >= threshold_line[i+1]:
                cross_up = i
                i += 1
                while i < line_length and line[i] >= threshold_line[i]: i += 1
                cross_down = i
                cross_point_groups.push_back(pair[int,int](cross_up,cross_down))
            else:
                i += 1
        cross_I = 0
        num_groups = cross_point_groups.size()
        if num_groups == 0:
            with gil:
                return []
        while cross_I < num_groups:
            if True: #line[cross_point_groups[cross_I].first] < line_threshold:
                event_start = cross_point_groups[cross_I].first
                event_end  = cross_point_groups[cross_I].second
                slice_max = -1.0
                slice_min = 1e10
                for i in range(event_start, event_end):
                    if line[i] > slice_max:
                        slice_max = line[i]
                    if line[i] < slice_min:
                        slice_min = line[i]
                if event_end - event_start > 1 and slice_max - slice_min > tolerance:
                    center = ((<double>event_start)+(<double> event_end))/2.0
                    split = ((<double> event_end) - (<double>event_start))/2.0
                    scaled = split*(1.0)
                    event_start = <int> max(0.0,center - scaled)
                    event_end = <int> min(line_length-1.0,scaled+center)
                    events2.push_back(pair[int,int](event_start,event_end))
            cross_I += 1
        cross_I = 0
        num_groups = events2.size()
        while cross_I < num_groups - 1:
            group1 = events2[cross_I]
            group2 = events2[cross_I+1]
            w1 = group2.first - group1.second
            w2 = group1.second - group1.first
            w3 = group2.second - group2.first
            k = group1.second
            slice_max = -1.0
            for i in range(group1.second,group2.first):
                slice_max = max(slice_max,threshold_line[i] - line[i])
            if (w1 < w2 or w1 < w3) and (slice_max < tolerance):
                if events.size() > 0 and events.back().second == group1.second:
                    events[events.size()-1] = pair[int,int](events.back().first,group2.second)
                else:
                    events.push_back(pair[int,int](group1.first,group2.second))
                cross_I += 2
            elif w1 < 2*(w2+w3) and slice_max < tolerance/1.5:
                if events.size() > 0 and events.back().second == group1.second:
                    events[events.size()-1] = pair[int,int](events.back().first,group2.second)
                else:
                    events.push_back(pair[int,int](group1.first,group2.second))
                cross_I += 2
            else:
                events.push_back(group1)
                cross_I += 1
        if events2.size() > 0 and events.size() > 0 and events[events.size()-1].second != events2[events2.size()-1].second:
            events.push_back(events2[events2.size()-1])
    ret = []
    i = 0
    for i in range(0,events.size()):
        if max_length != -1 and events[i].second - events[i].first > max_length:
            print(events[i].second-events[i].first)
            s,e = old_trimmer(line[events[i].first:events[i].second],max_length)
            ret.append([s+events[i].first,e+events[i].first])
        else:
            slc = [events[i].first,events[i].second]
            ret.append(slc)
    return ret


cpdef find_peaks(np.ndarray[np.float64_t,ndim=1] y, int min_width, double min_height):
    cdef int i,j,k
    cdef np.ndarray[np.float64_t,ndim=1] dy = y[1:] - y[:len(y)-1]
    cdef np.ndarray[np.float64_t,ndim=1] ddy = dy[1:] - dy[:len(dy)-1]
    cdef int line_length = len(y)
    cdef int min_wid2 = min_width/2
    cdef double diff_y = 0.0
    cdef double avg = 0.0
    cdef vector[int] maxes
    j = min_wid2
    while j+min_wid2 < line_length:
        diff_y = ((y[j]-y[j-min_wid2]) + (y[j] - y[j+min_wid2]))/2.0
        if diff_y > min_height:
            k = 0
            for i in range(j-min_wid2,j+min_wid2):
                avg += y[i]
                if y[i] > y[k]:
                    k = i
            # if avg/min_width < 0:
            maxes.push_back(k)
            j += min_wid2
        else:
            j += 1
    cdef np.ndarray[np.int32_t,ndim=1] ret = np.ndarray(maxes.size(),dtype=np.int32)
    for j in range(0,maxes.size()): ret[j] = maxes[j]
    return maxes



cpdef caustic_crossing(np.float64_t[:] &x,double x0, double s, double d,double x_factor,double vert_shift):
    cdef np.ndarray[np.float64_t,ndim=1] ret = np.zeros_like(x)
    cdef int i = 0
    cdef int x_length = len(x)
    cdef double sd2 = s/d/2.0
    cdef double ds4 = 4.0*d/s
    cdef double z, zd
    for i in range(0,x_length):
        z = x_factor*x[i] - x0
        zd = z/d
        if z > sd2:
            ret[i] = ds4*(sqrt(zd+sd2) - sqrt(zd-sd2))
        elif z > -sd2:
            ret[i] = ds4*sqrt(zd+sd2)
    return ret + vert_shift

cdef double min_array(np.float64_t[:] &a,int s, int e) nogil:
    cdef double minn = 1e10
    cdef int i
    for i in range(s,e):
        if a[i] < minn:
            minn = a[i]
    return minn


cpdef prominences(np.float64_t[:] &curve,np.int64_t[:] &peaks):
    cdef:
        int flag = 0
        double peak_height = 0.0
        np.ndarray[np.float64_t,ndim=1] ret = np.zeros_like(peaks,dtype=np.float64) * 1e10
        int i, j, k,I
        double slice_min
        int peaks_sz = peaks.shape[0]
        int curve_sz = curve.shape[0]
    for j in range(0,peaks_sz):
        I = peaks[j]
        peak_height = curve[I]
        i = 1
        k = 1
        flag = 0
        while flag == 0:
            flag = 1
            if k == 1 and I + i < curve_sz:
                flag = 0
                if curve[i+I] > peak_height:
                    ret[j] = curve[I] - min_array(curve,I,i+I)
                    k = 0
            if k == 1 and I - i >= 0:
                flag = 0
                if curve[I-i] > peak_height:
                    ret[j] = curve[I] - min_array(curve,I-i,I)
                    k = 0
            i += 1
    return ret

cpdef trimmed_to_size_slice(np.float64_t[:] &curve,int slice_length):
    cdef int center, index, i, j
    cdef double tmp, max_found
    cdef int curve_length = len(curve)
    center = 0
    max_found = -1.0
    for i in range(curve_length):
        if curve[i] > max_found:
            max_found = curve[i]
            center = i
    index = center - slice_length
    for i in range(max(center - slice_length,0),center):
        tmp = 0.0
        max_found = -1.0
        for j in range(i,min(i+slice_length,curve_length)):
            tmp += curve[j]
        if tmp > max_found:
            max_found = tmp
            index = i
    return [index,min(index+slice_length,curve_length)]

def old_trimmer(y,slice_length):
        center = np.argmax(y)
        max_found = -1.0
        index = center - slice_length
        for i in range(max(index,0),center):
            tmp = y[i:min(i+slice_length,len(y))].sum()
            if tmp > max_found:
                index = i
                max_found = tmp
        return [index,min(index+slice_length,len(y))]







    # cross_point_groups = []
    # i = 0
    # while i < len(smooth_deriv_abs)-1:
    #     if smooth_deriv_abs[i] < deriv_threshold and smooth_deriv_abs[i+1] >= deriv_threshold:
    #         # print("Found first upper")
    #         cross_up = i+1
    #         i += 1
    #         while i < len(smooth_deriv_abs) and smooth_deriv_abs[i] > deriv_threshold: i += 1
    #         cross_down = i-1
    #         cross_point_groups.append([cross_up,cross_down])
    #     else:
    #         i += 1
    # line_threshold = line.mean()+tolerance
    # events = []
    # cross_I = 0
    # while cross_I < len(cross_point_groups):
    #     if line[cross_point_groups[cross_I][0]] < line_threshold:
    #         event_start = cross_point_groups[cross_I][0]
    #         event_end = None
    #         #use a while True: if flag: break to emulate a do while loop
    #         while True:
    #             event_end = cross_point_groups[cross_I][1]
    #             if line[event_end] < line_threshold: 
    #                 break
    #             else:
    #                 cross_I += 1
    #         if event_end - event_start > 0 and line[event_start:event_end].max() > line_threshold:
    #             center = (event_start+event_end)/2
    #             split = (event_end - event_start)/2
    #             scaled = split*(1+tail_factor)
    #             event_start = max(0,int(center - scaled))
    #             event_end = min(len(line)-1,int(center+scaled))
    #             events.append([event_start,event_end])
    #     cross_I += 1
    # event_slices = list(map(lambda event: line[event[0]:event[1]], events))
    # return (events,event_slices)