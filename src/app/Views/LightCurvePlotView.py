'''
Created on Jul 25, 2017

@author: jkoeller
'''
from .View import CanvasView
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem


class LightCurvePlotView(CanvasView):
    '''
    classdocs
    '''


    def __init__(self, modelID='default',title=None, *args, **kwargs):
        '''
        Constructor
        '''
        CanvasView.__init__(self,modelID,title )
        self._plot = PlotItem()
        self.addItem(self._plot)
        self.title = "Light Curve"
        self.type = "LightCurveView"
        
    def plot(self,x,y,clear=True,pen={'width':5},**kwargs):
        self._plot.plot(x, y,clear=clear,pen=pen,**kwargs)
        
    def update(self,args):
        self.plot(*args)