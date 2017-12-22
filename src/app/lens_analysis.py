'''
Module for analyzing data produced by lensing_simulator. 

Contains decorator classes for file objects for fetching data.

The class :class:`Trial` contains most of the functionality for fetching data from a trial. Features include:
  - Fetching of a :class:`Parameters <app.Parameters.Parameters>` instance for how the simulation was set up.
  - Plotting of a magnification map with a :class:`MagMapView <app.Views.MagMapView.MagMapView>` view.
  - Fetching a light curve from the simulation or magnification map data.
  - Generating a FITS file from magnification map data.
  - Histogram of pixel values from magnification map data.

Below is an example of how to use the module for getting a magnification map as a FITS file.

>>> import lens_analysis as la
# Create a Experiment class instance, wrapping 'filename.dat'
>>> data = la.load('filename.dat') 
# Fetch the first trial in the file as a Trial instance.
>>> trial1 = data[0]
# Save the trial's magnification map to a FITS file
>>> trial1.getFitsFile('filename.fits')

 
'''

import copy
import glob
import os
import sys

from .parameters.ExperimentParams import LightCurveParameters, \
    MagMapParameters, StarFieldData
import numpy as np
from .calculator.ExperimentResultCalculator import varyTrial

sys.path.append(os.path.abspath('.'))



def __EventLoopActive():
    from PyQt5 import QtWidgets
    if QtWidgets.QApplication.instance():
        return True
    else:
        return False

def _requiresGUI(fn):
    def decorator(*args,**kwargs):
        if __EventLoopActive():
            return fn(*args,**kwargs)
        else:
            print("Must have Qt5 Event Loop initialized. To initialize, run the command \n\n>>> %gui qt5 \n\n")
    setattr(decorator,'__doc__',getattr(fn,'__doc__'))
    return decorator


def _requiresDtype(dtype):
    def decorator(fn):
        def decorated(self,*args,**kwargs):
            for k,v in self._exptTypes.items():
                if isinstance(k, dtype):
                    index = v
                    return fn(self,index,*args,**kwargs)
            raise AttributeError("Trial does not contain "+str(dtype) +" data.")
        setattr(decorated,'__doc__',getattr(fn, '__doc__'))
        return decorated
    return decorator




class AbstractFileWrapper(object):
    '''
    Abstract class, with methods for interracting with 'dat' files and directories containing them.
    Initialize AbstractFileWrapper object.
    
    Parameters:
    
    - `filepath`: (:class:`str`) path to file or directory of interest
    - `fileobject`: (file-like object) file object, if file is already opened. Default: :class:`None`
    - `params`: (:class:`Parameters`) Parameters object instance contained in the file. Passing in offers a slight optimization. Default: :class:`None`
    - `lookuptable` : (:class:`np.ndarray`) Array with byte shift for each data set present in the file. Passing in offers a slight optimization. Default: :class:`None`
     
    '''


    def __init__(self, filepath, fileobject=None, params=None, lookuptable=[]):
        '''
        '''
        self._filepath = filepath
        if not fileobject or not params:
            from .Controllers.FileManagerImpl import ExperimentDataFileReader
            reader = ExperimentDataFileReader()
            reader.open(self._filepath)
            self._params, self._fileobject = reader.load()
            reader.close()
        else:
            self._fileobject = fileobject
            self._params = params
        if lookuptable == []:
            self._lookupTable = np.load(self._fileobject)
        else:
            self._lookupTable = lookuptable
        self._exptTypes = {}
        for i in range(0,len(self._params.extras.desiredResults)):
            self._exptTypes[self._params.extras.desiredResults[i]] = i


    def _getDataSet(self,trialNo,tableNo):
        '''
        Internal method for retrieving a specific data table from the file. Uses the passed in trialNo and tableNo as row and column indices for the lookup table.
        
        Offers a low-level way of getting a numpy array out of a `*.dat` file.
        
        
        Parameters:
        
        - `trialNo`: (`<int>`) Specify the trial number of interest.
        - `tableNo`: (`<int>`) Specify which data set collected by the experiment to report.
        
        Returns: :class:`<np.ndarray>`
        '''
        self._fileobject.seek(self._lookupTable[trialNo,tableNo])
        return np.load(self._fileobject)
    
    def prettyPath(self,filename):
        
        '''
        Prints the filename of the passed in string, removing the path and giving only the filename itself.
        
        Parameters:
        
        - 'filename': (:class:`str`) Filename to clean up and return.
        
        Returns: `str`
        '''
        prettyString = filename
        while prettyString.partition('/')[2] != "":
            prettyString = prettyString.partition('/')[2]
        return prettyString
    
    def has(self,restype):
        '''
        Return whether or not the experiment type specified by `restype` is represented in the data file.
        
        Returns: :class:'bool'
        '''
        return restype in self._exptTypes

    @property
    def file(self):
        '''
        Returns the file-like object this :class:`AbstractFileWrapper` decorates.
        '''
        return self._fileobject
    
    @property
    def filename(self):
        '''
        Returns the name of the file-like object this :class:`AbstractFileWrapper` decorates
        '''
        return self.prettyPath(self._filepath)
    
    @property
    def describe(self):
        '''
        Prints the system parameters along with a description of all the data enclosed within the file.
        '''
        print(str(self))
        
    @property
    def parameters(self):
        '''
        Returns an instance of the parameters specified by the file.
        '''
        return self._params
        
        
    def __str__(self):
        return str(self._params)




class DirectoryMap(object):
    '''
    Class for processing all the files in a directory at once. If the directory contains many file types, 
    will filter out all the files except those with the `.dat` extension. Allows for accessing files by filename, with syntax like that of a :class:`dict`
    or by numeric index. Files sorted numerically by time since the file was created, with newest last. Supports for loop comprehensions.

    Accessing a specific file automatically returns the file, decorated as a :class:`Experiment`.

    Parameters:
    dirname (:class:`str`): Directory to decorate. Relative to the current directory.
    '''


    def __init__(self, dirname):
        '''
        Constructor
        '''
        self.__directory = dirname
        files = filter(os.path.isfile,glob.glob(self.__directory + "/*.dat"))
        self.__files = []
        for fille in files:
            self.__files.append(fille)
        self.__files.sort(key = lambda x: os.path.getmtime(x))
        self.__index = 0

    def __len__(self):
        return len(self.__files)
    
    @property
    def size(self):
        '''
        Number of `.dat` files in the directory.
        '''
        return len(self)
    
    @property
    def length(self):
        '''
        Alias of :func:`size`.
        '''
        return len(self)
    
    @property
    def directory(self):
        '''
        Returns the directory this :class:`DirectoryMap` decorates.
        '''
        return self.__directory
    
    
    @property
    def describe(self):
        '''
        Prints name of all the enclosed files.
        '''
        print(str(self))
        
        
    def __str__(self):
        ret = ""
        for file in self.__files:
            ret += file
            ret += "\n"
        return ret
    
    def __getitem__(self,ind):
        if isinstance(ind,int):
            if ind < len(self.__files):
                return Experiment(self.__files[ind])
            else:
                raise IndexError("Index out of range.")
        elif ind in self.__files:
            return Experiment(self.__files[self.__files.index(ind)])
        else:
            raise IndexError("Invalid index of DirectoryMap instance. Index must be a number or filename.")
        
    def __iter__(self):
        return DirectoryMap(self.__directory)
    
    def __next__(self):
        if self.__index < self.size:
            try:
                ret = Experiment(self.__files[self.__index])
                self.__index += 1
                return ret
            except:
                self.__index = 0 
        else:
            self.__index = 0
            raise StopIteration
        
    
class Experiment(AbstractFileWrapper):
    '''
    Decorator for a '.dat' file. To construct use the :func:`lens_analysis.load <app.lens_analysis.load>` function, or from indexing or for-looping through a :class:`DirectoryMap <app.lens_analysis.DirectoryMap>` instance.

    This class provides simple ways to describe the data generated by a simulation. Can print the description of the experiment, gives access to the parameters of the system, and indexing into it returns specific trials in the form of a :class:`Trial <app.lens_analysis.Trial>` instances.
    '''


    def __init__(self, filepath, fileobject=None,params=None,lookuptable=[]):
        '''
        Constructor
        '''
        AbstractFileWrapper.__init__(self,filepath,fileobject,params,lookuptable)
        self.__index = 0
        

    
    def __next__(self):
        if self.__index < len(self._lookupTable):
            ret =  Trial(self._filepath,self.__index,self._fileobject,self._params,self._lookupTable)
            self.__index += 1
            return ret 
        else:
            self.__index = 0
            raise StopIteration
            
    def __getitem__(self,ind):
        if isinstance(ind,int):
            if ind < len(self._lookupTable):
                return Trial(self._filepath,ind,self._fileobject,self._params,self._lookupTable)
            else:
                raise IndexError("Index out of range.")
        else:
            raise ValueError("Index must be of type int")

    def __len__(self):
        return len(self._lookupTable)
        



    @property
    def size(self):
        '''
        Returns the number of trials in the experiment.
        '''
        return len(self)
    
    @property
    def length(self):
        '''
        See :func:`size`.
        '''
        return len(self)

    @property
    def numTrials(self):
        '''
        See :func:`size`.
        '''
        return self.length
        
        
    
    def __iter__(self):
        return Experiment(self._filepath,self._fileobject,self._params,self._lookupTable)
        


class Trial(AbstractFileWrapper):
    '''
    Class providing convenient ways to interract with data generated by one trial of a gravitationally lensed system.
    This is the workhorse class of the :class:`lens_analysis` module. Provides the methods for accessing data, getting statistical info, 
    etc.

    Can be constructed directly, but recommended to construct by indexing a :class:`la.Experiment` instance.
    '''
    def __init__(self,filepath,trialno,fileobject=None,params=None,lookuptable=[]):
        AbstractFileWrapper.__init__(self, filepath, fileobject, params, lookuptable)    
        self.__trialNo = trialno
    
    
    @property
    @_requiresDtype(LightCurveParameters)
    def lightCurve(self,ind,xUnit = 'arcsec'): #Automatically passed in parameter 'ind' supplies information of what column that data type is located in
        '''
        Requires the trial have light curve data.

        Returns a tuple containing the X and Y axes of a light curve run. X axis represents distance traveled by quasar, Y axis represents magnfication coefficient.

        Parameters: `xUnit` (:class:`str`) Unit to measure the x axis in. 
        '''
        lc = self._getDataSet(ind)
        x = np.arange(0,len(lc))
        distCovered = self.parameters.extras.desiredResults[ind].pathEnd - self.parameters.extras.desiredResults[ind].pathStart
        dist = distCovered.to(xUnit).magnitude()/len(lc)
        x = x * dist
        return (x,lc)
    
    
    @_requiresDtype(MagMapParameters)
    def getFitsFile(self,ind,filename = None,**kwargs):
        '''
        Constructs a FITS file for visualizing the trial's magnification map data. Requires the trial contain magnification map data.

        Parameters:

        `filename` (:class:`str`): File to save the FITS data to. If none is open, attempts to open a file dialog to prompt the user.
        Additional arguments passed in will be inserted into the FITS file's header. The keyword supplied becomes a new field in the 
        header, and the argument is converted to a string and given as that field's body.
        '''
        from .Controllers.FileManagerImpl import FITSFileWriter
        arr = self._getDataSet(ind)
        fm = FITSFileWriter()
        fm.open(filename)
        fm.write(arr,**kwargs)
        fm.close()
        print("Magnification Map saved")

    @_requiresDtype(StarFieldData)
    def getStars(self,ind):
            return self._getDataSet(ind)

    # @_requiresDtype(StarFieldData)
    # @_requiresDtype(MagMapParameters)
    # def superimpose_stars(self,magIndex,starsIndex,magmapimg=None,destination=None,color = (255,255,0,255)):
    #     '''DEPRECATED'''
    #     parameters = self.regenerateParameters()
    #     from PIL import Image
    #     img = Image.open(magmapimg)
    #     pix = img.load()
    #     stars = parameters.galaxy.stars
    #     dTheta = parameters.extras.desiredResults[magIndex].dimensions.to('rad')/parameters.extras.desiredResults[magIndex].resolution
    #     starCoords = stars[:,0:2]
    #     starMass = stars[:,2]
    #     starCoords[:,0] = starCoords[:,0]/dTheta.x + parameters.extras.desiredResults[magIndex].resolution.x/2
    #     starCoords[:,1] = starCoords[:,1]/dTheta.y + parameters.extras.desiredResults[magIndex].resolution.y/2
    #     # starCoords[:,0] = starCoords[:,0]*dTheta.x/parameters.dTheta.to('rad').value
    #     # starCoords[:,1] = starCoords[:,1]*dTheta.y/parameters.dTheta.to('rad').value
    #     starCoords = np.ascontiguousarray(starCoords,dtype=np.int32)
    #     for row in range(0,starCoords.shape[0]):
    #         x,y = (starCoords[row,0],starCoords[row,1])
    #         mass = starMass[row]
    #         r = int(math.sqrt(mass+2))
    #         for i in range(x-r,x+r):
    #             for j in range(y-r,y+r):
    #                 if i >= 0 and i < parameters.extras.desiredResults[magIndex].resolution.x and j >= 0 and j < parameters.extras.desiredResults[magIndex].resolution.y:
    #                     pix[j,i] = color
    #     img.save(destination)
    #     print("Superimposed image saved as "+destination)

    @_requiresDtype(StarFieldData)
    def regenerateParameters(self,ind):
        '''
        Constructs and returns a :class:`app.Parameters` instance, exactly as it was when the :class:`Trial` was calculated.
        '''
        params = copy.deepcopy(self.parameters)
        stars = self.getStars()
        params.setStars(stars)
        return params    
    @property
    def parameters(self):
        params = copy.deepcopy(self._params)
        params =  varyTrial(params,self.trialNumber)
        stars = self.getStars()
        params.setStars(stars)
        return params
        

    def histogram(self,numBuckets=100,fn='linear'):
        '''
        Constructs a histogram from the :class:`Trial`'s data. Requires the instance contain Magnification map data.
        
        Parameters:
            `numBuckets` (:class:`int`): Number of buckets to divide the data into. Defaults to 100.
            
        Returns:
            Tuple of the counts calculated and buckets used (`counts,buckets`). 
        '''
        mm = self.magMap
        if fn == 'log10':
            mm = np.log10(mm+0.0000000001)
        ret = np.histogram(mm,numBuckets+1)
        return (ret[0],ret[1][1:])
        
    @_requiresDtype(StarFieldData)
    @_requiresDtype(MagMapParameters)
    def traceQuasar(self,magIndex,starsIndex):
        '''
        DEPRECATED
        '''
        magnifications = self._getDataSet(magIndex)
        params = self.regenerateParameters()
        return (magnifications,params)
        
    # def saveParameters(self,filename=None):
    #     '''DEPRECATED'''
    #     from ..Controllers.FileManagerImpl import ParametersFileManager
    #     saver = ParametersFileManager()
    #     if filename:
    #         saver.write(copy.deepcopy(self.parameters),filename)
    #     else:
    #         saver.write(copy.deepcopy(self.parameters))
    #     print("parameters Saved")
        
    @property
    def trialNumber(self):
        '''
        Returns this trial's index within the experiment calculated.
        '''
        return self.__trialNo

#    @property
#    def parameters(self):
#        '''
#        See :class:`regenerateParameters`
#        '''
#        try:
#            return self.regenerateParameters()
#        except AttributeError:
#            return AbstractFileWrapper.parameters

    
    
    @property
    def datasets(self):
        '''
        Returns a generator, iterating through the different data sets enclosed in the trial.
        '''
        index = 0
        while index < self._lookupTable.shape[1]:
            yield self._getDataSet(self.__trialNo, index)
            
    @property
    @_requiresDtype(MagMapParameters)
    def magMap(self,ind):
        '''
        Requires Magnification Map data. Returns the magnification map data as a numpy array.
        '''
        return self._getDataSet(ind)
            
            
    def _getDataSet(self,tableNo):
        '''
        Internal Method. Allows access to any dataset at the given index in the lookup table.
        '''
        self._fileobject.seek(self._lookupTable[self.__trialNo,tableNo])
        return np.load(self._fileobject)
  












def load(filename='Untitled.dat'):
    '''
    Given a filename, returns a :class:`la.Experiment` (if a `.dat` file is provided) or a :class:`la.DirectoryMap`
    (if a directory name is provided) instance generated from the specified file. If filename is None, and a Qt event loop 
    is running, opens a file dialog to specify the file.

    Parameters:
    
    - `filename` (:class:`str`) : Filename to look up. Defaults to '`Untitled.dat`'. If None is passed in, opens a dialog to specify the file.
    '''
    if filename is None:
        from PyQt5 import QtWidgets
        filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.dat')[0]
    if filename:
        lngth = len(filename)
        if filename[lngth-4::] == '.dat':
            return Experiment(filename)
        else:
            return DirectoryMap(filename)
    else:
        return None

def describe(filename):
    '''
    Convenience function for getting information about a file.

    Given a `.dat` filename, prints the file's description. This method is equivalent to calling:

    >>> import lens_analysis as la
    >>> data_to_describe = la.load('file.dat')
    >>> data_to_describe.describe

    Parameters: `filename` (:class:`str`) : The data file to describe. Must have a `.dat` extension. Also accepts any subtype of :class:`la.AbstractFileWrapper`.
    '''
    if isinstance(filename, str) and filename[len(filename)-4::] == '.dat':
        tmp = load(filename)
        tmp.describe
    elif isinstance(filename, AbstractFileWrapper):
            filename.describe
    else:
        raise ValueError("argument must be a filename or AbstractFileWrapper subtype.")

# def traceQuasar(expt,trialNum=0):
#     from PyQt5 import QtWidgets
#     from ..Views.GUI.GUITracerWindow import GUITracerWindow
#     app = QtWidgets.QApplication(sys.argv)
#     if isinstance(expt,str):
#         ui = GUITracerWindow(expt,trialNum=trialNum)
#         ui.show()
#     else:
#         ui = GUITracerWindow(expt.file.name,expt.trialNumber)
#         ui.show()
#     app.exec_()
# 
# def explore(expt):
#     params = None
#     if isinstance(expt,AbstractFileWrapper):
#         params = expt.parameters
#     elif isinstance(expt, Parameters):
#         params = expt
#     else:
#         raise ValueError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
#         return
#     if not params:
#         return ValueError("Argument must be an AbstractFileWrapper subtype or Parameters instance")
#         return
#     try:
#         ui = GUIManager()
#         ui.switchToVisualizing()
#         ui.bindFields(params)
#         ui.switchToVisualizing()
#         ui.show()
#     except:
#         raise EnvironmentError("Must have a Qt event loop running. If you are in ipython, execute the command '%gui qt5' then try again.")

@_requiresGUI
def visualizeMagMap(model=None):
    '''
        Spawns and returns an instance of a :class:`app.Views.MagMapView`. If a model argument is supplied, will load the supplied model(s) into the view upon initialization.
        Parameters:

        - `model`: (:class:`la.Trial`,:class:`la.Experiment`, or :class:`str`) Model(s) to be loaded in upon initialization of the view. If `model` is a `str`, will assume the string is a filename which designates a `*.dat` file to load in.

    '''
    from .Views.MainView import MainView
    import GUIMain
    ui = MainView()
    GUIMain.bindWindow(ui)
    magMapViewController = GUIMain._addMagPane(ui)
    ui.show()
    if model:
        magMapViewController.setModel(model)
    return magMapViewController

