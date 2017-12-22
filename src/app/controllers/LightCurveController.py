'''
Created on Dec 20, 2017

@author: jkoeller
'''
from . import Controller


class LightCurveController(Controller):
    '''
    Controller for managing a light curve. 
    '''


    def __init__(self, *args,**kwargs):
        '''
        Constructor
        '''
        Controller.__init__(self,*args,**kwargs)
        from app.views import PlotView
        self._viewType = PlotView
        
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType), "view must be a PlotView instance for LightCurveController to bind to it."
        self.signals['view_update_signal'].connect(view.update_slot)
        
    def plot_xy(self,x,y):
        self.signals['view_update_signal'].emit({'xAxis':x,'yAxis':y})
        
        
        
        