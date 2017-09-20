'''
Created on Jul 28, 2017

@author: jkoeller
'''
from PyQt5 import QtWidgets


class FileWriter(object):
    '''
    Provides an interface for exporting data to files.
    Has three public methods:
    
    parameters:
        fileExtension:
            string argument specifying the file extension. For example,
            '.dat', '.fits', '.mp4' are possible extensions.
            Defaults to emptystring, in which case no extensions is appended
            to file names.
        
        
    
    
    
    
    def open(*args,**kwargs):
        opens a file, either by opening a dialog or with the 
        supplied name. Must be called before writing any data.
        
    def write(*args,**kwargs):
        Takes in data, and writes to file/buffers it as appropriate.
        This function handles most of the actual work of the file
        manager.
        
    def close(*args,**kwargs):
        Closes the file, saving all to disk. Calling this method finalizes
        all file interraction, until the file manager is used again with
        a call to the 'open' function.
        Must be call this method, else risk corrupting data.
        
        
        
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
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass 

    def getFile(self,filename=None,*args,**kwargs):
        if filename:
            if self._fileextension in filename:
                self._filename=filename
            else:
                print(type(filename))
                self._filename = filename+self._fileextension
        else:
            self._filename = QtWidgets.QFileDialog.getSaveFileName(filter='*'+self._fileextension)[0]
        return self._filename
    
    def open(self, filename=None, *args,**kwargs):
        filename = self.getFile(filename)
        
    @property
    def _fileextension(self):
        return ''
        
        
    def write(self,*args,**kwargs):
        pass 
    
    def close(self,*args,**kwargs):
        pass
    
    
class FileReader(object):
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
            self._filename = QtWidgets.QFileDialog.getOpenFileName(filter='*'+self._fileextension)[0]
        return self._filename

    def load(self, filename=None, *args,**kwargs):
        filename = self.getFile(filename)
        
    @property
    def _fileextension(self):
        return ''
