'''
Created on Jul 25, 2017

@author: jkoeller
'''

class Controller(object):
    '''
    Abstract object for calculating. Accepts a list of delegates to perform each step,
    along with a senderDelegate that sends the produced data off to export to file,
    the screen, etc.
    
    ___________________
    
    Methods:
    
    calculate(*args,**kwargs)
        Method to be called to perform the Controller's role. Must return something,
        even if it is None.
    '''
    _children = []

    def __init__(self):
        '''
        Constructor
        '''
        self._children = []
        # for child in children:
        #     self.addChild(child)
        
    def calculate(self,*args):
        """"Method to be called to execute the controller's work. calls all delegates first,
        and lastly feeds what they return into execute, returning whatever execute has been overridden
        to return."""
        return args

    def run(self,*args):
        args = self.calculate(*args)
        for child in self._children:
            child.run(args)


    def addChild(self, child):
        self._children.append(child)

    @property
    def children(self):
        return str(self._children)
    