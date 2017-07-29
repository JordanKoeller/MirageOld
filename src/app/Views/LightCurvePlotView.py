'''
Created on Jul 25, 2017

@author: jkoeller
'''
from .CanvasView import CanvasView
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem


class LightCurvePlotView(CanvasView):
    '''
    classdocs
    '''


    def __init__(self, modelID, *args, **kwargs):
        '''
        Constructor
        '''
        CanvasView.__init__(self,modelID,*args,**kwargs)
        self._plot = PlotItem()
        self.addItem(self._plot)
        self.title = "Light Curve"
        self._signalRef.connect(self.update)
        
    def plot(self,x,y,clear=True,pen={'width':5},**kwargs):
        self._plot.plot(x, y,clear=clear,pen=pen,**kwargs)
        
    def update(self,args,kwargs={}):
        self.plot(*args,**kwargs)