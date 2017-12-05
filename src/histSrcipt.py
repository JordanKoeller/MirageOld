import numpy as np
from astropy.io import fits
from matplotlib import pyplot as pl
import os

def avgFitsFiles(directory,bins):
    fFiles = []
    nonF = []
    for ff in os.listdir(directory):
        ff = os.fsdecode(ff)
        if ".fits" in ff:
            fFiles.append(ff)
        elif ".png" not in ff:
            nonF.append(ff)
    print(fFiles)
    data = map(lambda f: fits.open(directory+"/"+f)[0].data,fFiles)
    nonF = fits.open(directory+"/"+nonF[0])[0].data
    hists = map(lambda x:np.histogram(np.log10(x+0.000001),bins),data)
    histCtrl,ctrBucs = np.histogram(0.4*(1024-nonF)/64+0.000001,bins)
    vals = []
    buckets = []
    for y, x in hists:
        yFix = y
        buckets.append(x[1:])
        vals.append(yFix)
    return (buckets,vals,ctrBucs[1:],histCtrl)


def plotStuff(directory,bins):
    plt, ax = pl.subplots()
    bucs, avg, bc, ac = avgFitsFiles(directory,bins)
    for i in range(0,len(bucs)):
        pl.plot(bucs[i],avg[i],label = "Trial")
    ax.plot(bc,ac,label = "Control")
    ax.set_title(str(masses[int(directory)])+"% Stars")
    pl.show()
    pl.legend()
    pl.savefig(directory+"/"+str(masses[int(directory)])+".png",bbox_inches="tight")
        
