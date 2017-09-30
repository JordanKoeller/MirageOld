'''
Created on Jun 2, 2017

@author: jkoeller
'''

from PyQt5 import QtCore
from PyQt5.Qt import QPushButton

from pyqtgraph.widgets.TableWidget import TableWidget

from ..Utility.NullSignal import NullSignal


class ExperimentQueueTable(TableWidget):


    editingSignal = QtCore.pyqtSignal(object,int)

    def __init__(self,parent=None,editable = True): 
        """ datain: a list of QueueEntries
            headerdata: a list of strings
        """
        TableWidget.__init__(self,parent,editable=editable)
        self.__experiments = []
        self.__initClearTable()

        
    def addExperiment(self, experiment):
        self.experiments.append(experiment)
        txtRow = self.__mkRow(experiment)
        TableWidget.addRow(self, txtRow)
        exptButton = QPushButton()
        exptButton.setText("Edit")
        exptButton.setMinimumWidth(50)
        exptButton.clicked.connect(lambda: self.editingSignal.emit(experiment,self.numRows-1))
        self.setCellWidget(self.numRows,len(txtRow),exptButton)
        clearButton = QPushButton()
        clearButton.setText("Remove")
        clearButton.setMinimumWidth(50)
        clearButton.clicked.connect(lambda: self.removeItem(experiment))
        self.setCellWidget(self.numRows,len(txtRow)+1,clearButton)

    def removeItem(self,expt):
        tmp = self.experiments[:]
        self.clear()
        self.__initClearTable()
        self.__experiments = []
        for i in tmp:
            if i is not expt:
                self.addExperiment(i)


    def clearTable(self):
        self.__initClearTable()
        
    def updateExperiment(self,exp,num):
        self.experiments[num] = exp
        tmp = self.experiments[:]
        self.clear()
        self.__initClearTable()
        self.__experiments = []
        for i in tmp:
            self.addExperiment(i)
            
    def __initClearTable(self):
        self.setData([["","","","",""]])
        headers = ['Name','Description','Number of Trials','Parameters','Remove']
        self.setColumnWidth(0,100)
        self.setColumnWidth(1,400)
        self.setColumnWidth(2,130)
        self.setColumnWidth(3,100)
        self.setColumnWidth(4,100)
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalHeaderLabels(headers)
        self.__experiments = []
                  
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