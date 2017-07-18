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

from app.Views.GUI.GUITracerWindow import GUITracerWindow

if __name__ == "__main__":
    print('____________________________\n\n\n'+"Process ID = " + str(os.getpid())+'\n\n\n____________________________')

    app = QtWidgets.QApplication(sys.argv)
    
    ui = GUITracerWindow()
    ui.show()

    sys.exit(app.exec_())