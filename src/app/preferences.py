'''
Created on Jul 25, 2017

@author: jkoeller
'''

import json 
import multiprocessing
import os
import numpy as np

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
        _PreferencesParser.__init__(self,os.environ['projectDir']+'.custom_preferences.json')
        if self['core_count'] == 'all':
            self._prefMap['core_count'] = multiprocessing.cpu_count()
        if self['use_openCL']:
            if self['cl_device'] != 'discover':
                os.environ['PYOPENCL_CTX'] = str(self['cl_device'])
        if self['color_scheme']:
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
GlobalPreferences = _GlobalPreferences()
