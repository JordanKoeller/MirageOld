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

    def __init__(self,view):
        '''
        Constructor
        '''
        QtCore.QObject.__init__(self)
        self.view = view
        
    def __del__(self):
        self.hide()
        
    def show(self):
        pass
    
    def hide(self):
        pass
    
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