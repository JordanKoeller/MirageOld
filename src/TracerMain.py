'''
Created on Jul 17, 2017

@author: jkoeller
'''

'''
Created on May 31, 2017

@author: jkoeller
'''
import os
import sys
from PyQt5 import QtWidgets
import argparse
from app.Views.GUI.GUITracerWindow import GUITracerWindow


if __name__ == "__main__":
    print('____________________________\n\n\n'+"Process ID = " + str(os.getpid())+'\n\n\n____________________________')

    parser = argparse.ArgumentParser()
    parser.add_argument("--run",nargs='+', type=str, help='Follow with a .params infile and outdirectory to save data to.')

    app = QtWidgets.QApplication(sys.argv)

    if args.run:
    	fname = args.run[0]
    	tNum = int(args.run[1])
	    ui = GUITracerWindow(fname,tNum)
	    ui.show()
	else:
	    ui = GUITracerWindow()
	    ui.show()

    



    sys.exit(app.exec_())