'''
Created on May 31, 2017

@author: jkoeller
'''
import os
import sys

import argparse

def usingMPI():
    try:
        from mpi4py import MPI
        
        comm = MPI.COMM_WORLD
        sz = comm.Get_size()
        return sz > 0
    except:
        return False
    
def isMainProcess():
    if not usingMPI():
        return True
    else:
        try:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            return comm.Get_rank() == 0
        except:
            return False
    
processPool = []

if __name__ == "__main__" and isMainProcess():
    print('____________________________ \n\n'+"Process ID = " + str(os.getpid())+'\n\n____________________________')

    parser = argparse.ArgumentParser()
    parser.add_argument("--load",nargs='?', type=str, help='Follow with a .param file to load in as parameters.')
    parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')
    parser.add_argument("-v","--visualize",action='store_true',help='Launch program in visualization perspective.')
    parser.add_argument("-q","--queue",action='store_true',help='Launch program in experiment queue perspective.')
    args = parser.parse_args()
    

    if args.run:
        sys.stdout = open(os.devnull,'w')
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
        print('____________________________ \n\n Caluations Finished \n\n____________________________')
        sys.exit()
    else:
        from PyQt5 import QtWidgets
        from app.Views.MainView import MainView as GUIManager
        app = QtWidgets.QApplication(sys.argv)
        ui = GUIManager()
        if args.queue:
            ui.switchToQueue()
        else:
            pass
            # ui.switchToVisualizing()
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
    
else:
    #Add subprocesses to processPool
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    print("Adding process "+str(comm.Get_rank()) + " To the Pool.")
#     processPool.append(comm)
    fn = None
    data = comm.recv(source=0,tag=11)
    print(data)
#     print("Accepting")
    if type(isinstance(data,list)):
        fn = data[0]
        try:
            fn(data[1])
        except:
            pass
    else:
        fn(data)
    






        
