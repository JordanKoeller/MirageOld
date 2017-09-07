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
        
    run(*args)
        Method that recurses through all delegates, calling their respective calculate methods. 
        If self is deactivated before, by calling self.deactivate(), this method does nothing.
        
    addChild(delegate)
        adds child to this instance's children. This controller will now call delegate.calculate() when 
        looping through its children.
        
    deactivate()
        Deactivate this controller. After calling this method, calls to self.run() will do nothing, and will not 
        recurse down to its children. If the controller is already deactivated, this does nothing.
    
    activate()
        Reactivates this controller, allowing calls to self.run() to execute. If the controller is already active,
        this does nothing.
        
    ____________________
    
    Attributes:
    
    children: list[Controller] 
    '''
    _children = []

    def __init__(self):
        '''
        Constructor. No Arguments.
        '''
        self._children = []
        self._active = True
        # for child in children:
        #     self.addChild(child)
        
    def calculate(self,*args):
        """"Method to be called to execute the controller's work. calls all delegates first,
        and lastly feeds what they return into execute, returning whatever execute has been overridden
        to return."""
        return args

    def run(self,*args):
        '''
        Method that recurses through all delegates, calling their respective calculate methods. 
        
        If self is deactivated before, by calling self.deactivate(), this method does nothing.
        '''
        if self._active:
            args = self.calculate(*args)
            for child in self._children:
                child.run(*args)


    def addChild(self, child):
        if isinstance(child,Controller):
            self._children.append(child)
        else:
            raise ValueError("child mustbe of type Controller")
            
            
    def deactivate(self):
        """
        Deactivate this controller. After calling this method, calls to self.run() will do nothing, and will not 
        recurse down to its children. If the controller is already deactivated, this does nothing.
        """
        self._active = False
        
    def activate(self):
        """
        Reactivates this controller, allowing calls to self.run() to execute. If the controller is already active,
        this does nothing.
        """
        self._active = True

    @property
    def children(self):
        return str(self._children)
    