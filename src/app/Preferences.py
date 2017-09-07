'''
Created on Jul 25, 2017

@author: jkoeller
'''

import json 
import multiprocessing
import os
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
        


class _GlobalPreferences(_PreferencesParser):
    """docstring for _GlobalPreferences"""
    def __init__(self):
        _PreferencesParser.__init__(self,'Resources/.default_global_preferences.json')
        if self['core_count'] == 'all':
            self._prefMap['core_count'] = multiprocessing.cpu_count()
        if self['use_openCL']:
            if self['cl_device'] != 'discover':
                os.environ['PYOPENCL_CTX'] = str(self['cl_device'])


GlobalPreferences = _GlobalPreferences()
TracerPreferences = _PreferencesParser('Resources/.default_tracer_preferences.json')

