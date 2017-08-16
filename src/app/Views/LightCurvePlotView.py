'''
Created on Jul 25, 2017

@author: jkoeller
'''
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem

from .CompositeView import CompositePlot
from .View import CanvasView


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
        # self.title = "Light Curve"
        self.type = "LightCurveView"
        
    def plot(self,x,y,clear=True,pen={'width':5},**kwargs):
        self._plot.plot(x, y,clear=clear,pen=pen,**kwargs)
        
    def update(self,args):
        self.plot(*args)

    def setBridge(self,bridge):
        print("Bridging")
        self._bridge = bridge

    def bridgeTo(self,view):
        if not self._bridge and not view._bridge:
            CompositePlot(self,view)
            # view.setBridge(self._bridge)
        elif not self._bridge:
            view._bridge.addView(self)
        else:
            self._bridge.addView(view)
            # view.setBridge(self._bridge)
