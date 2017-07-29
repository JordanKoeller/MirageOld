'''
Created on Jul 25, 2017

@author: jkoeller
'''

import json 

class _PreferencesParser(object):
    '''
    classdocs
    '''
    fileLoc = ''
    _prefMap = {}
    
    def __init__(self,filename):
        '''
        Constructor
        '''
        self.fileLoc = filename
        with open(self.fileLoc,encoding='utf-8') as file:
            data = json.load(file)
            self._prefMap = data
            print(self._prefMap)
        
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
        

GlobalPreferences = _PreferencesParser('Resources/.default_global_preferences.json')
TracerPreferences = _PreferencesParser('Resources/.default_tracer_preferences.json')