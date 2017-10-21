'''
Created on May 31, 2017

@author: jkoeller
'''
from PyQt5 import QtCore


class GUIController(QtCore.QObject):
    '''
    classdocs
    '''
    thread = None
    fileManager = None
    view = None
    extrasBinder = None
    extrasBuilder = None

    def __init__(self,view,binder=None,builder=None):
        '''
        Constructor
        '''
        QtCore.QObject.__init__(self)
        self.view = view
        self.extrasBinder = binder
        self.extrasBuilder = builder
        
#     def __del__(self):
#         self.hide()
        
    def show(self):
        pass
    
    def hide(self):
        pass
    
    def bindFields(self,*args,**kwargs):
        pass

    @property
    def modelID(self):
        return self.view.modelID
    
#     @property
#     def signals(self):
#         '''
#         Attribute returning the signals associated with a controller.
#         '''
#         pass
#     
#     @property
#     def slots(self):
#         '''
#         Attribute returning the slots asssociated with a controller 
#         '''
#         pass