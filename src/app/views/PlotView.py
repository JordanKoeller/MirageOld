'''
Created on Dec 19, 2017

@author: jkoeller
'''


from pyqtgraph.widgets.PlotWidget import PlotWidget

from . import View


class PlotView(View):
    '''
    classdocs
    '''


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        View.__init__(self,*args,**kwargs)
        self._plot = PlotWidget()
        self.addWidget(self._plot)
        self.setTitle("PlotView")
        self._pen = {'width':5}
        
    def update_slot(self, args):
        '''
        Method called to update the plot. In this case, arguments to specify how to draw a line plot.
        
        Parameters:
        
        - args (:class:`dict`) : a `dict` with at least two fields - "xAxis" and "yAxis". "yAxis" may be a list, in which case all the arrays within will be overlaid. Any extra fields within `args` will be passed along to the :class:`PlotWidget.plot` function.
        
        Returns:
        
        - N/A
        
    
        '''
        assert type(args) is dict, 'PlotView did not receive a dict while calling update.'
        assert 'xAxis' in args, 'PlotView did not receive an x-axis'
        assert 'yAxis' in args, 'PlotView did not receive any y-axis'
        xAxis = args['xAxis']
        yAxis = args['yAxis']
        del args['xAxis']
        del args['yAxis']
        if 'pen' not in args:
            args['pen'] = self._pen
        if type(yAxis) is list:
            self._plot.clear()
            for dset in yAxis:
                self._plot.plot(xAxis,dset,**args)
        else:
            self._plot.plot(xAxis,yAxis,clear=True,**args)
    
        