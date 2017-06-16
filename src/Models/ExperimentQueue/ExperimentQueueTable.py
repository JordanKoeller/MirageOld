'''
Created on Jun 2, 2017

@author: jkoeller
'''

from pyqtgraph.widgets.TableWidget import TableWidget
from PyQt5.Qt import QPushButton
from Utility.NullSignal import NullSignal


class ExperimentQueueTable(TableWidget): 
    def __init__(self, signal=NullSignal,parent=None,editable = True): 
        """ datain: a list of QueueEntries
            headerdata: a list of strings
        """
        TableWidget.__init__(self,parent,editable=editable)
        self.signal = signal
        self.__experiments = []
        self.__initClearTable()

        
    def addExperiment(self, experiment):
        self.experiments.append(experiment)
        txtRow = self.__mkRow(experiment)
        TableWidget.addRow(self, txtRow)
        exptButton = QPushButton()
        exptButton.setText("Edit")
        exptButton.setMinimumWidth(50)
        exptButton.clicked.connect(lambda: self.signal.emit(experiment,self.numRows-1))
        self.setCellWidget(self.numRows,len(txtRow),exptButton)
        
    def updateExperiment(self,exp,num):
        self.experiments[num] = exp
        tmp = self.experiments[:]
        self.clear()
        self.__initClearTable()
        self.__experiments = []
        for i in tmp:
            self.addExperiment(i)
            
    def __initClearTable(self):
        self.setData([["","","",""]])
        headers = ['Name','Description','Number of Trials','Parameters']
        self.setColumnWidth(0,100)
        self.setColumnWidth(1,400)
        self.setColumnWidth(2,130)
        self.setColumnWidth(3,100)
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalHeaderLabels(headers)
            
                  
    def __mkRow(self,params):
        experiment = params.extras
        return [experiment.name,experiment.desc,experiment.numTrials]
    
    @property
    def experiments(self):
        return self.__experiments
    
    def __len__(self):
        return len(self.experiments)

        
    @property
    def numRows(self):
        return len(self.experiments)