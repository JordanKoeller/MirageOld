'''
Created on May 31, 2017

@author: jkoeller
'''
import argparse
from datetime import datetime as DT
import logging
import os
import sys

def run_simulation(files):
    # sys.stdout = open(os.devnull,'w')
    from app.calculator import ExperimentTableRunner
    from app.io import TableFileReader, ExperimentDataFileWriter
    infile = files[0]
    outfile = files[1]
    queueThread = ExperimentTableRunner()
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
    timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
    logging.info('\n\n Caluations Finished in ' + timeString)
    sys.exit()

def visualize():
    from PyQt5 import QtWidgets
    from app.views import WindowView
    from app.controllers import MasterController
    from app.model import ParametersModel
    app = QtWidgets.QApplication(sys.argv)
    model = ParametersModel()
    view = WindowView()
    controller = MasterController()

    controller.bind_to_model(model)
    controller.bind_view_signals(view)
    view.show()
    sys.exit(app.exec_())




if __name__ == "__main__":
    print("Program initialized.")
    print('____________________________ \n\n'+"Process ID = " + str(os.getpid())+'\n\n____________________________')
    starttime = DT.now()

    parser = argparse.ArgumentParser()
    parser.add_argument("--load",nargs='?', type=str, help='Follow with a .param file to load in as parameters.')
    parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')
    parser.add_argument("--log",nargs='+', type=str, help='File to dump logging info to. Defaults to a file named after the date and time the program was initialized.')
    parser.add_argument("-v","--visualize",action='store_true',help='Launch program in visualization perspective.')
    args = parser.parse_args()
    if args.log:
        logging.basicConfig(filename=args.log[0],level=logging.INFO)
    if not args.run and not args.visualize:
        visualize()
    if args.run:
        run_simulation(args.run)
    else:
        visualize()








