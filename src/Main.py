'''
Created on May 31, 2017

@author: jkoeller
'''
import os
import sys
from PyQt5 import QtWidgets

from app.Views.GUI.GUIManager import GUIManager
from app.Controllers.FileManagers.ParametersFileManager import ParametersFileManager
from app.Controllers.FileManagers.QueueFileManager import QueueFileManager
from app.Controllers.Threads.QueueThread import QueueThread
from app.Controllers.FileManagers.TableFileManager import TableFileManager

import argparse


if __name__ == "__main__":
    print('____________________________\n\n\n'+"Process ID = " + str(os.getpid())+'\n\n\n____________________________')

    parser = argparse.ArgumentParser()
    parser.add_argument("--load",nargs='?', type=str, help='Follow with a .param file to load in as parameters.')
    parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')
    parser.add_argument("-v","--visualize",action='store_true',help='Launch program in visualization perspective.')
    parser.add_argument("-q","--queue",action='store_true',help='Launch program in experiment queue perspective.')
    args = parser.parse_args()
    
    app = QtWidgets.QApplication(sys.argv)

    if args.run:
        infile = args.run[0]
        outfile = args.run[1]
        queueThread = QueueThread()
        fileLoader = TableFileManager()
        table = fileLoader.read(infile)
        fileWriter = QueueFileManager(directory=outfile)
        queueThread.bindExperiments(table,fileWriter)
        queueThread.run()
        sys.exit()
    else:
        ui = GUIManager()
        if args.queue:
            ui.switchToQueue()
        else:
            ui.switchToVisualizing()
        ui.show()
        if args.load:
            paramLoader = ParametersFileManager()
            params = paramLoader.read(args.load)
            ui.switchToVisualizing()
            ui.bindFields(params)
            # Model.updateParameters(params)

    sys.exit(app.exec_())
    






        
