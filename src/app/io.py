'''
Created on Dec 26, 2017

@author: jkoeller
'''

import json
import numpy as np


from app.preferences import GlobalPreferences
from app.utility import asynchronous

from abc import ABC, abstractmethod

class FileWriter(ABC):
    '''
Abstract class providing an interface for exporting data to file. Has two methods that must be overwritten, along with some convenience functions. The abstract methods are:

    - :func:`write`
    - :func:`close`

Additionally, to give the files an extension, overwrite the :func:`_fileextension` property.

To write the data, the protocol is defined below:

>>> filename = "file.extension"
>>> filewriter.open(filename) #If no filename is provided, will try to open a QDialog to select a file.
>>> filewriter.write(data)
>>> filewriter.close()
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass 

    def getFile(self,filename=None,*args,**kwargs):
        '''
Convenience function for setting the FileWriter's file. If no filename is provided, this function opens a QFileDialog so the user may select a file. The QFileDialog will be restricted in what files to choose by the string returned by the property :func:`_fileextension`.Must be called before calling :func:`write`.
        '''
        if filename:
            if self._fileextension in filename:
                self._filename=filename
            else:
                self._filename = filename+self._fileextension
        else:
            from PyQt5 import QtWidgets
            self._filename = self._addExt(QtWidgets.QFileDialog.getSaveFileName(filter='*'+self._fileextension)[0])
        return self._filename
    
    def _addExt(self,filename):
        if self._fileextension in filename:
            return filename
        else:
            return filename+self._fileextension
    
    def open(self, filename=None, *args,**kwargs):
        '''
Opens a file with the specified `filename`. If none is supplied, opens a dialog to prompt the user to select a file by calling :func:`getFile`
        '''
        filename = self.getFile(filename)
        
    @property
    def _fileextension(self):
      '''
Override with the file extension the :class:`FileWriter` will write. Defaults to emptystring.
      '''
      return ''
        
    @abstractmethod
    def write(self,*args,**kwargs):
        '''
Abstract method. When passed data, writes to file/buffers it as appropriate. This function handles most of the actual work of the file manager. 
        '''
        pass 

    @abstractmethod
    def close(self,*args,**kwargs):
        '''
Closes the file, saving all to disk. Calling this method finalizes all file interraction, until the file manager is used again with a call to the 'open' function. Must call this method, else risk corrupting data.
        '''
        pass
    
    
class FileReader(ABC):
    """
Provides an interface for loading data from files.
    Has three public methods:
    
    parameters:
        fileExtension:
            string argument specifying the file extension. For example,
            '.dat', '.fits', '.mp4' are possible extensions.
            Defaults to emptystring, in which case no extensions is appended
            to file names.
        
        
    
    
    
    
    def load(*args,**kwargs):
        opens a file, either by opening a dialog or with the 
        supplied name. Must be called before writing any data.
        
        
    for subclassing:
        two additional functions are important:
        
        def getFile(fname):
            checks for a supplied filename. If a supplied filename exists (or the
            variable self._filename is defined from initialization) then it returns that
            filename as a string. Otherwise, it opens a Qt.FileChooser dialog, returning the
            filename specified with proper extension. This method also sets 
            self._filename to whatever was chosen. By default, this is called by the 
            'open' method.
           
        @property
        def _fileextension(self):
            returns a string of the file extension, such as '.mp4' or '.png'.
            Defaults to empty string. Must be overridden.
    
    """
    
    def __init__(self,*args,**kwargs):
        pass
    
    def open(self,filename=None,*args,**kwargs):
        return self.getFile(filename) is not None

    def getFile(self,filename=None,*args,**kwargs):
        if filename:
            if self._fileextension in filename:
                self._filename=filename
            else:
                self._filename = filename+self._fileextension
        else:
            from PyQt5 import QtWidgets
            self._filename = QtWidgets.QFileDialog.getOpenFileName(filter='*'+self._fileextension)[0]
            if self._filename == "": self._filename = None
        return self._filename

    def load(self, filename=None, *args,**kwargs):
        filename = self.getFile(filename)
        
    @property
    def _fileextension(self):
        return ''

def _formatJson(data):
    ret = json.dumps(data,indent=4)
    return ret

class RecordingFileManager(FileWriter):
    
    
    def __init__(self,buffer_frames=False):
        FileWriter.__init__(self)
        self._bufferFrames = buffer_frames
        
    def _asNPArray(self,im):
        im = im.toImage()
        im = im.convertToFormat(4)
        width = im.width()
        height = im.height()
        ptr = im.bits()
        ptr.setsize(im.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        arr2 = arr.copy()
        arr[:,0] = arr2[:,2]
        arr[:,2] = arr2[:,0]
        return arr
        
    def open(self, filename=None, *args, **kwargs):
        FileWriter.open(self, filename=filename, *args, **kwargs)
        import imageio
        self._writer = imageio.get_writer(self._filename,fps=GlobalPreferences['max_frame_rate'])
        self._frames = []
    
    def write(self, frame):
        if self._bufferFrames:
            self._frames.append(frame)
        else:
            frame = self._asNPArray(frame)
            self._writer.append_data(frame)
            
    @property
    def _fileextension(self):
        return '.mp4'
            
    @asynchronous
    def close(self):
        print("File saved")
        if self._bufferFrames:
            for frame in self._frames:
                img = self._asNPArray(frame)
                self._writer.appendData(img)
            self._frames = []
        self._writer.close()


class ParametersFileManager(FileWriter):
    '''
    classdocs
    '''

    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        FileWriter.__init__(self)

    def open(self, filename=None):
        FileWriter.open(self, filename)
        if self._filename:
            self._file = open(self._filename,'w+')
            return True
        else:
            return False
        
    def write(self, data):
        jsonString = _formatJson(data.jsonString)
        self._file.write(jsonString)

    def close(self):
        self._file.close()
        self._file = None
        
    @property
    def _fileextension(self):
        return '.param'

class ParametersFileReader(FileReader):

    def __init__(self,*args,**kwargs):
        FileReader.__init__(self,*args,**kwargs)

    def open(self, filename=None):
        ret = FileReader.open(self,filename)
        print(ret)
        return ret

    def load(self):
        self._filename = self._filename or self.open()
        from app.parameters.Parameters import ParametersJSONDecoder
        self._file = open(self._filename)
        model = json.load(self._file)
        decoder = ParametersJSONDecoder()
        model = decoder.decode(model)
        return model

    def close(self):
        self._file.close()
    
    @property
    def _fileextension(self):
        return '.param'

class TableFileWriter(FileWriter):
    
    def __init__(self):
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self,filename)

    def write(self,data):
        if self._filename:
            self._file = open(self._filename,'wb+')
            dataStrings = []
            for i in data:
                dataStrings.append(i.jsonString)
            js = _formatJson(dataStrings)
            self._file.write(bytes(js,'utf-8'))
        
    def close(self):
        self._file.close()
        
    @property
    def _fileextension(self):
        return '.params'
    
class TableFileReader(FileReader):
    
    def __init__(self):
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self,filename)

    def load(self):
        if self._filename:
            from app.parameters.Parameters import ParametersJSONDecoder
            decoder = ParametersJSONDecoder()
            self._file = open(self._filename,'rb+')
            data = self._file.read()
            paramList = json.loads(data)
            ret = []
            for p in paramList:
                ret.append(decoder.decode(p))
            return ret
        
    def close(self):
        pass        
        
    @property
    def _fileextension(self):
        return '.params'

class ModelFileReader(FileReader):
    """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
    def __init__(self):
        super(ModelFileReader, self).__init__()
        

    def load(self,filename=None,*args,**kwargs):
        if self._filename:
            from app.parameters.Parameters import ParametersJSONDecoder
            self._file = open(self._filename)
            model = json.load(self._file)
            decoder = ParametersJSONDecoder()
            model = decoder.decode(model)
            if model:
                return model
            else:
                return None
        else:
            return None

    @property
    def _fileextension(self):
        return '.param'

# class ModelFileWriter(FileWriter):
#     """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
#     def __init__(self):
#         super(ModelFileWriter, self).__init__()
        
#     @property
#     def _fileextension(self):
#         return '.param'

#     def write(self,data):
#         if self._filename:
#             self._file = open(self._filename,'wb+')
#             pickle.dump(data,self._file)
#         else:
#             self.open()
#             self.write(data)

class ExperimentDataFileWriter(FileWriter):
    """docstring for ExperimentDataFileWriter"""
    def __init__(self):
        super(ExperimentDataFileWriter, self).__init__()
        
    def open(self,filename=None):
        self._directory = filename or self.getDirectory()
        self.exptFile = None
        self.pickledParams = None
        self.dataSizeArray = None
        self.dataSizeLoc = None
        self.trialCount = 0
        self.experimentCount = 0 #Specifies which row in the table to be written next
        self._name = self._directory
        self._parametersWriter = ParametersFileManager()

    def getDirectory(self):
        from PyQt5 import QtWidgets
        directory = QtWidgets.QFileDialog.getExistingDirectory()
        return directory

    def newExperiment(self,params):
        name = params.extras.name
        filename = self.directory+'/'+name+'.dat'
        self.exptFile = open(filename,'wb+')
        self.dataSizeArray = self.getDataSizeArray(params) #TODO
        jsonString = _formatJson(params.jsonString)
        self.exptFile.write(bytes(jsonString,'utf-8'))
        self.exptFile.write(b'\x93')
        self.parametersEndLoc = self.exptFile.tell()
        self.trialCount = 0
        np.save(self.exptFile,self.dataSizeArray)

    def closeExperiment(self):
        self._updateDataSizeArray()
        self.exptFile.flush()
        self.exptFile.close()
        #Class data cleanup
        self.exptFile = None
        self.pickledParams = None
        self.dataSizeArray = None
        self.dataSizeLoc = None
        self.trialCount = 0
        self.experimentCount += 1

    def getDataSizeArray(self,params):
        numtrials = params.extras.numTrials
        numDataPoints = len(params.extras.desiredResults)
        ret = np.zeros((numtrials,numDataPoints),dtype=np.int64)
        return ret

    def _updateDataSizeArray(self):
        self.exptFile.flush()
        tmploc = self.exptFile.tell()
        self.exptFile.seek(self.parametersEndLoc,0)
        np.save(self.exptFile,self.dataSizeArray)
        #Stream cleanup
        self.exptFile.flush()
        self.exptFile.seek(tmploc,0)


    def write(self,data):
        for i in range(0,len(data)):
            self.dataSizeArray[self.trialCount,i] = self.exptFile.tell() - self.parametersEndLoc
            np.save(self.exptFile,data[i])
        self._updateDataSizeArray()
        self.trialCount += 1

    def getPretty(self,string):
        prettyString = string
        divisions = prettyString.split('/')
        last = divisions[len(divisions)-1]
        return last

    def flush(self):
        if self.exptFile:
            self.exptFile.flush()
            
    def close(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()

    @property
    def _fileextension(self):
        return '.dat'

    @property
    def name(self):
        return self._name 
    
    @property
    def directory(self):
        return self._directory

    @property
    def prettyName(self):
        return self.getPretty(self.name)

    def __del__(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()
            
        
class ExperimentDataFileReader(FileReader):


    def __init__(self):
        FileReader.__init__(self)

    def open(self,filename=None):
        self._filename = filename or self.getFile()

    def load(self):
        with open(self._filename,'rb+') as file:
            import tempfile
            from app.parameters.Parameters import ParametersJSONDecoder
            paramsJSON, data = file.read().split(b'\x93',maxsplit=1)
            dataFile = tempfile.TemporaryFile()
            dataFile.write(data)
            decoder = ParametersJSONDecoder()
            paramsDict = json.loads(paramsJSON)
            params = decoder.decode(paramsDict)
            dataFile.seek(0)
            return (params,dataFile)

    def close(self):
        pass




class FITSFileWriter(FileWriter):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        FileWriter.__init__(self)
        

    def open(self,filename = None):
        self._filename = filename or self.getFile()

    def write(self,data,**headerFields):
        from astropy.io import fits
        header = fits.Header(headerFields)
        hdu = fits.PrimaryHDU(data,header=header)
        hdulist = fits.HDUList([hdu])
        hdulist.writeto(self._filename)
        
    def close(self):
        pass
        
    @property
    def fileextension(self):
        return ".fits"
