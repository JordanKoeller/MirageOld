'''
Created on May 31, 2017

@author: jkoeller
'''
import os
import sys

import argparse
from datetime import datetime as DT

import logging



if __name__ == "__main__":
    print("Program initialized.")
    print('____________________________ \n\n'+"Process ID = " + str(os.getpid())+'\n\n____________________________')
    logging.basicConfig(filename='progress.log',level=logging.INFO)
    starttime = DT.now()

    parser = argparse.ArgumentParser()
    parser.add_argument("--load",nargs='?', type=str, help='Follow with a .param file to load in as parameters.')
    parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')
    parser.add_argument("--log",nargs='+', type=str, help='File to dump logging info to. Defaults to a file named after the date and time the program was initialized.')
    parser.add_argument("-v","--visualize",action='store_true',help='Launch program in visualization perspective.')
    parser.add_argument("-q","--queue",action='store_true',help='Launch program in experiment queue perspective.')
    args = parser.parse_args()
    
    if args.log:
        logging.basicConfig(filename=args.log[0],level=logging.INFO)
    else:
        logging.basicConfig(filename=str(starttime.isoformat())+".log",level=logging.INFO)


    if args.run:
#        sys.stdout = open(os.devnull,'w')
        from app.Controllers.ExperimentTableRunner import ExperimentTableRunner as QueueThread
        from app.Controllers.FileManagerImpl import TableFileReader, ExperimentDataFileWriter
        infile = args.run[0]
        outfile = args.run[1]
        queueThread = QueueThread()
        fileLoader = TableFileReader()
        fileLoader.open(infile)
        table = fileLoader.load()
        fileLoader.close()
        fileWriter = ExperimentDataFileWriter()
        fileWriter.open(outfile)
        queueThread.bindExperiments(table,fileWriter)
        queueThread.run()
        endTime = DT.now()
        dSec = (endTime - starttime).seconds
        hrs = dSec // 3600
        mins = (dSec // 60) % 60
        secs = dSec % 60
        timeString = str(hrs)+" hr, " + str(mins) + " min, " + str(secs)
        logging.info('____________________________ \n\n Caluations Finished in' + timeString + ' . \n\n____________________________')
        sys.exit()
    else:
        from PyQt5 import QtWidgets
        from app.views.MainView import MainView as GUIManager
        import GUIMain 
        app = QtWidgets.QApplication(sys.argv)
        ui = GUIManager()
        GUIMain.bindWindow(ui)
        GUIMain._showVisSetup(ui)
        ui.show()
        if args.load:
            from app.Controllers.FileManagerImpl import ParametersFileReader
            paramLoader = ParametersFileReader()
            paramLoader.open(args.load)
            params = paramLoader.load()
            paramLoader.close()
            ui.switchToVisualizing()
            ui.bindFields(params)
    sys.exit(app.exec_())






        
