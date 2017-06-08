'''
Created on Jun 7, 2017

@author: jkoeller
'''

from lens_analysis.AbstractFileWrapper import AbstractFileWrapper



class Trial(AbstractFileWrapper):
    def __init__(self,filepath,trialno,fileobject=None,params=None,lookuptable=None):
        AbstractFileWrapper.__init__(self, filepath, fileobject, params, lookuptable, None)    
        self.__trialNo = trialno
        

    @property
    def datasets(self):
        index = 0
        while index < self._lookupTable.shape[1]:
            yield self.getDataSet(self.__trialNo, index)
    
#     @property
#     def experiment(self):
#         return Experiment(self.__filepath,self.__fileobject,self.__params,self.__lookupTable,self.__resultType)
#         
#     def __iter__(self):
#         return self
#     
#     def __next__(self):
#         pass
#         