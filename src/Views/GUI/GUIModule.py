'''
Created on May 31, 2017

@author: jkoeller
'''

class GUIModule(object):
    '''
    classdocs
    '''


    def __init__(self,controller):
        """
        Constructor
        """
        self.controller = controller
        self.controller.setup(self)
        self.setup()
    
    def setup(self):
        """
        Abstract method. Called upon initialization of a GUI type.
        """
        pass
    
    def start(self):
        pass
        