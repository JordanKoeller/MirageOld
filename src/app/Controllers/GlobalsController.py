

__boundWindows = []

#Model = ModelImpl()



def bindWindow(view):
#         if isinstance(view, WindowFrame):
        view.playPauseAction.triggered.connect(_playPauseToggle)
        view.resetAction.triggered.connect(_resetHelper)
        view.saveTableAction.triggered.connect(_saveTable)
        view.loadTableAction.triggered.connect(_loadTable)
        # view.parametersEntryHelpAction.triggered.connect(???)
        view.actionAddCurvePane.triggered.connect(_addCurvePane)
        view.actionAddImgPane.triggered.connect(_addImgPane)
        view.actionAddMagPane.triggered.connect(_addMagPane)
        view.actionAddParametersPane.triggered.connect(_addParametersPane)
        # view.actionAddTablePane.triggered.connect(view.addTablePane)
        view.save_setup.triggered.connect(_saveSetup)
        view.load_setup.triggered.connect(_loadSetup)
        view.record_button.triggered.connect(_toggleRecording)
        view.visualizerViewSelector.triggered.connect(_showVisSetup)
        view.queueViewSelector.triggered.connect(_showTableSetup)
        view.tracerViewSelector.triggered.connect(_showTracerSetup)
        view.actionConfigure_Models.triggered.connect(_openModelDialog)
        view.actionExport.triggered.connect(_exportLightCurves)
        view.recordSignal.connect(_recordWindow)
        __boundWindows.append(view)
#         else:
#             raise ValueError("window must be a WindowFrame instance")

def _playPauseToggle(window):
      print("PP")

def _resetHelper(window):
      print("RESET")

def _saveTable(window):
      pass

def _loadTable(window):
      pass

def _addCurvePane(window):
      pass

def _addImgPane(window):
      pass

def _addMagPane(window):
      pass

def _addParametersPane(window):
      pass

def _saveSetup(window):
      pass

def _loadSetup(window):
      pass

def _toggleRecording(window):
      pass

def _showVisSetup(window):
      pass

def _showTableSetup(window):
      pass

def _showTracerSetup(window):
      pass

def _openModelDialog(window):
      pass

def _exportLightCurves(window):
      pass

def _recordWindow(window):
      pass

