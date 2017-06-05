'''
Created on May 31, 2017

@author: jkoeller
'''
import os
import sys

from PyQt5 import QtWidgets

from Views import GUIManager


if __name__ == "__main__":
    print('____________________________\n\n\n'+"Process ID = " + str(os.getpid())+'\n\n\n____________________________')
    args = sys.argv
    app = QtWidgets.QApplication(sys.argv)
    if len(args) == 1:
        ui = GUIManager()
        ui.switchToVisualizing()
        ui.show()
    elif len(args) == 2:
        arg = args[1]
        if arg == "Visualize" or arg == "visualize" or arg == "Vis" or arg == "vis":
            ui = GUIManager()
            ui.switchToVisualizing()
            ui.show()
#         elif arg == "Stats" or arg == "stats" or arg == "stat" or arg == "Stat":
#             pass
#             ui = GUIManager(StatsController())
#             ui.show()
        elif arg == "Queue" or arg == "queue" or arg == "q" or arg == "Q":
            ui = GUIManager()
            ui.switchToQueue()
            ui.show()
        else:
            print("Error. Invalid Command Line Argument.")
            sys.exit(0)
    else:
        print("Error. Invalid Command Line Argument.")
        sys.exit(0)
    sys.exit(app.exec_())
        