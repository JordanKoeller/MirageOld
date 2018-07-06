'''
Created on Jul 25, 2017

@author: jkoeller
'''

import json 
import multiprocessing
import os
import numpy as np
import random 
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

    def items(self):
        return self._prefMap.items()
        


class _GlobalPreferences(_PreferencesParser):
    """docstring for _GlobalPreferences"""
    def __init__(self,path):
        _PreferencesParser.__init__(self,path)
        defaults = _PreferencesParser(os.environ['projectDir']+'.default_preferences.json')
        #Load in defaults
        for k,v in defaults.items():
            if k not in self._prefMap:
                self._prefMap[k] = v
        self._prefMap['path'] = os.environ['projectDir']
        #Convert from keywords to settings, etc.
        if self['core_count'] == 'all':
            self._prefMap['core_count'] = multiprocessing.cpu_count()
        if self['use_openCL']:
            if self['cl_device'] != 'discover':
                os.environ['PYOPENCL_CTX'] = str(self['cl_device'])
        lookup = {
            'minimum':1,
            'saddle_pt':5,
            'galaxy':4,
            'star':2,
            'quasar':3,
            'background':0
            }
        global ColorMap
        for color in self['color_scheme'].items():
            c = color[1][1:]
            c1 = c[0:2]
            c2 = c[2:4]
            c3 = c[4:6]
            r = int(c1,16)
            g = int(c2,16)
            b = int(c3,16)
            ColorMap[lookup[color[0]]] = [r,g,b]



ColorMap = np.ndarray((6,3), dtype = np.uint8)
GlobalPreferences = _GlobalPreferences(os.environ['projectDir']+'.custom_preferences.json')

