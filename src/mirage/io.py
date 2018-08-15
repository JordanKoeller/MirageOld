'''
Created on Dec 26, 2017

@author: jkoeller
'''

import json
import numpy as np
import tempfile
import zipfile
import shutil
import os 

from mirage.preferences import GlobalPreferences

from abc import ABC, abstractmethod



def _formatJson(data):
    ret = json.dumps(data,indent=4)
    return ret




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


class ParametersFileManager(FileWriter):
    '''
    classdocs
    '''

    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        FileWriter.__init__(self)

    def open(self, filename=None,file_object=None):
        if file_object:
            self._filename = file_object.name
            self._file = file_object
            return True
        else:
            FileWriter.open(self, filename)
            if self._filename:
                self._file = open(self._filename,'wb+')
                return True
            else:
                return False
        
    def write(self, data):
        jsonString = _formatJson(data.json)
        self._file.write(bytes(jsonString,'utf-8'))
        return True

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
        return ret

    def load(self,file_object=None):
        from mirage.parameters import Parameters
        if not file_object:
            self._filename = self._filename or self.open()
            self._file = open(self._filename,'rb')
        else:
            self._file = file_object
        ret_pt = self._file.tell()
        ending = self.find_end()
        self._file.seek(ret_pt)
        bites = self._file.read(ending - ret_pt)
        decoder = json.JSONDecoder()
        string = str(bites,'utf-8',errors="ignore")
        js,ind = decoder.raw_decode(string)
        model = Parameters.from_json(js)
        return model

    def find_end(self,end_char=b'\x93'):
        flag = True
        buf_sz = int(1e6)
        last_pt = self._file.tell()
        while flag:
            tmp = self._file.read(buf_sz)
            if end_char in tmp:
                flag = False
                ind = tmp.index(end_char)
                last_pt = last_pt + ind
            elif len(tmp) == 0:
                return last_pt
            else:
                last_pt = self._file.tell()
        return last_pt

    def close(self):
        self._file.close()
    
    @property
    def _fileextension(self):
        return '.param'


class SimulationWriter(FileWriter):

    def __init__(self) -> None:
        FileWriter.__init__(self)
    def open(self,filename:str="",file_object=None) -> None:
        if not file_object:
            self._file = None
            return FileWriter.open(self,filename)
        else:
            self._file = file_object
            return True

    def write(self,data):
        if not self._file:
            self._file = open(self._filename,'wb+')
        js = data.json
        string = _formatJson(js)
        self._file.write(bytes(string,'utf-8'))

    def close(self):
        self._file.close()

    @property 
    def _fileextension(self):
        return '.sim'

class SimulationReader(FileReader):

    def __init__(self) -> None:
        FileReader.__init__(self)

    def open(self,filename:str):
        FileReader.open(self,filename)

    def load(self):
        from mirage.parameters import Simulation
        self._file = open(self._filename,'rb')
        js = self._file.read()
        js = json.loads(js)
        return Simulation.from_json(js)

    def close(self):
        self._file.close()

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
                dataStrings.append(i.json)
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
            from mirage.parameters import Simulation
            self._file = open(self._filename,'rb')
            data = self._file.read()
            paramList = json.loads(data)
            ret = []
            for p in paramList:
                ret.append(Simulation.from_json(p))
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
            self._file = open(self._filename)
            model = json.load(self._file)
            model = Parameters.from_json(model)
            if model:
                return model
            else:
                return None
        else:
            return None

    @property
    def _fileextension(self):
        return '.param'


class ExperimentDataFileWriter(FileWriter):
    """docstring for ExperimentDataFileWriter"""
    def __init__(self):
        super(ExperimentDataFileWriter, self).__init__()
        
    def open(self,filename=None):
        self._directory = filename or self.getDirectory()
        self.trialCount = 0
        self.experimentCount = 0 #Specifies which row in the table to be written next
        self._simWriter = SimulationWriter()
        self._locationArray = None

    def getDirectory(self):
        from PyQt5 import QtWidgets
        directory = QtWidgets.QFileDialog.getExistingDirectory()
        return directory

    def new_experiment(self,num_trials,num_results):
        self.tempfile = tempfile.TemporaryFile()
        self._locationArray = self.getDataSizeArray(num_trials,num_results)
        self.trialCount = 0
        with tempfile.TemporaryFile() as tempfile2:
            np.save(tempfile2,self._locationArray)
            self._zeroMark = tempfile2.tell()


    def close_experiment(self,simulation):
        self.tempfile.flush()
        with open(self._directory + "/" + simulation.experiments.name + '.dat','wb+') as file:
            self._simWriter.open(file_object=file)
            self._simWriter.write(simulation)
            np.save(file,self._locationArray)
            #Now need to copy over tempfile contents
            self.tempfile.seek(0)
            file.write(self.tempfile.read())
        self.tempfile.close()
        self._locationArray = None
        self._zeroMark = 0
        self.trialCount = 0
        self.experimentCount += 1

    def getDataSizeArray(self,numtrials,numDataPoints):
        ret = np.zeros((numtrials,numDataPoints),dtype=np.int64)
        return ret


    def write(self,data):
        for i in range(0,len(data)):
            self._locationArray[self.trialCount,i] = self.tempfile.tell() + self._zeroMark
            np.save(self.tempfile,data[i])
        self.trialCount += 1

    def getPretty(self,string):
        prettyString = string
        divisions = prettyString.split('/')
        last = divisions[len(divisions)-1]
        return last

    def close(self):
        pass

    @property
    def _fileextension(self):
        return '.dat'

    @property
    def name(self):
        return self._directory
    
    @property
    def directory(self):
        return self._directory


    @property
    def prettyName(self):
        return self.getPretty(self.name)

    def __del__(self):
        pass

class ExperimentDataFileReader(FileReader):


    def __init__(self):
        FileReader.__init__(self)

    def open(self,filename=None):
        self._filename = filename or self.getFile()

    def load(self):
        file = open(self._filename,'rb')
        preader = ParametersFileReader()
        params = preader.load(file_object=file)
        offset = file.tell()
        print(offset)
        dataFile = tempfile.TemporaryFile()
        for chunk in iter(lambda: file.read(int(1e6)), b''):
            dataFile.write(chunk)
        dataFile.seek(0)
        return (params,dataFile)

    def close(self):
        pass

class ModelLoader(FileReader):
    """General-purpose file loader for reading files containing system descriptions.
    This class can read files with .param, and .params extensions and pull out
    just the Parameters object instance inside."""

    from mirage.parameters import Parameters

    _reader_delegates = {'.params': TableFileReader,
                         '.param': ParametersFileReader}

    def __init__(self):
        super(ModelLoader, self).__init__()
        self._fileDelegate = None

    def _get_extension(self,filename):
        return '.' + filename.split('.')[-1]

    def open(self,filename=None):
        self._filename = filename or self.getFile()
        extension = self._get_extension(self._filename)
        self._fileDelegate = self._reader_delegates[extension]()
        self._fileDelegate.open(self._filename)
    
    def load(self,index = 0):
        ret = self._fileDelegate.load()
        if isinstance(self._fileDelegate,ParametersFileReader):
            return ret
        else:
            return ret[index]

    def close(self):
        self._fileDelegate.close()
        self._fileDelegate = None



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


