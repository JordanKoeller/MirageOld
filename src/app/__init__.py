import sys
import os

abspath = os.path.abspath(__file__).split('src')[0]
os.environ['projectDir'] = abspath
os.environ['srcDir'] = abspath+'src/'
tracerUIFile = abspath+'Resources/TracerGUI/tracerwindow.ui'
mainUIFile = abspath+'Resources/gui.ui'
parametersUIFile = abspath+'Resources/GUIViews/ParametersView/parametersview.ui'
tableUIFile = abspath+'Resources/GUIViews/BatchTableView/batchtableview.ui'
magmapUIFile = abspath+'Resources/GUIViews/MagnificationMapView/magnificationmapview.ui'
modeldialogUIFile = abspath+'Resources/GUIViews/ConfigureModelsDialog/configuremodelsdialog.ui'


# __model = None
# 
# @property
# def Model():
#     assert __model is not None, "Must set the model before can interract with it."
#     return __model
# 
# def setModel(model):
#     from .model import _AbstractModel
#     assert isinstance(model,_AbstractModel)
#     __model = model
