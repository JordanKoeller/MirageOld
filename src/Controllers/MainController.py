'''
Created on May 31, 2017

@author: jkoeller
'''
import sys

from PyQt5 import QtWidgets

from Main import GUIManager

class Main(object):
    
    def __init__(self):
        import os
        print("Process ID = " + str(os.getpid()))
        app = QtWidgets.QApplication(sys.argv)
        ui = GUIManager()
        ui.show()
        sys.exit(app.exec_())