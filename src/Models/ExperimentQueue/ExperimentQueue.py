'''
Created on Jun 1, 2017

@author: jkoeller
'''

class ExperimentQueue(object):
    '''
    classdocs
    '''
    __experiments = []

    def __init__(self, directoryName):
        '''
        Constructor
        '''
        self.directoryName = directoryName
        
    def append(self, experiment):
        self.__experiments.append(experiment)
        
    def remove(self, num):
        # May try-catch for error here.
        self.__experiments.remove(self.experiments[num])
    
    def update(self, num, newExp):
        self.__experiments[num] = newExp
        
    @property
    def queue(self):
        return self.__experiments
    
    def makeTable(self,table):
        pass
    
    def run(self):
        pass
    
    def __len__(self):
        return len(self.__experiments)
    
    def __iter__(self):
        pass #TODO
    
    
