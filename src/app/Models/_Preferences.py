'''
Created on Jul 23, 2017
 
@author: jkoeller
'''

import json
 
class _Preferences(object):
    '''
    classdocs
    '''
    fileLoc = ''
    _prefMap = {}
    
    def __init__(self):
        '''
        Constructor
        '''
        file = open(self.fileLoc,encoding='utf-8')
        data = json.load(file.read())
        self._prefMap = data
        
    def __getitem__(self,key):
        if isinstance(key, str):
            try:
                return self._prefMap[key]
            except KeyError:
                raise KeyError("Preference Not Found")
        else:
            raise KeyError("Key Must Be a String")
        
    def updatePreferences(self,kv):
        self._prefMap.update(kv)
        json.dump(self._prefMap, open(self.fileLoc,'w+'))
        