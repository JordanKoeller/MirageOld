from PyQt5 import QtCore
from PyQt5.Qt import QObject
from PyQt5.QtWidgets import QInputDialog

from app.Controllers import ControllerFactory  # , ExportFactory
from app.Controllers.ParametersController import ParametersController
from app.Models import Model
from app.Views.LensedImageView import LensedImageView
from app.Views.LightCurvePlotView import LightCurvePlotView
from app.Views.MagMapView import MagMapView
from app.Views.ModelDialog import ModelDialog
from app.Views.ParametersView import ParametersView
from app.Views.TableView import TableView
from app.Views.View import CanvasView
import factory


from app.Models.MagnificationMapModel import MagnificationMapModel


class _UISignals(QObject):
    playSignal = QtCore.pyqtSignal()
    pauseSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    deactivateSignal = QtCore.pyqtSignal()
    recordSignal = QtCore.pyqtSignal()
    progressDialogSignal = QtCore.pyqtSignal(int, int, str)
    progressLabelSignal = QtCore.pyqtSignal(str)
    
    def __init__(self):
        QObject.__init__(self)

__boundWindows = []

__controllers = []

__UISignals = _UISignals()




def modelControllers():
    return __controllers

def views():
    ret = []
    for window in __boundWindows:
        for view in window.views:
            ret.append(view)
    return ret

def canvasViews():
    dvs = []
    for view in views():
        if isinstance(view,CanvasView):
            dvs.append(view)
    return dvs

def bindWindow(view):
        view.playPauseAction.triggered.connect(_playPauseToggle)
        view.resetAction.triggered.connect(_resetHelper)
        view.actionAddCurvePane.triggered.connect(lambda: _addCurvePane(view))
        view.actionAddImgPane.triggered.connect(lambda: _addImgPane(view))
        view.actionAddMagPane.triggered.connect(lambda: _addMagPane(view))
        view.actionAddParametersPane.triggered.connect(lambda: _addParametersPane(view))
        view.actionAddTablePane.triggered.connect(lambda: _addTablePane(view))
        view.record_button.triggered.connect(lambda: _toggleRecording(view))
        view.visualizerViewSelector.triggered.connect(lambda: _showVisSetup(view))
        view.queueViewSelector.triggered.connect(lambda: _showTableSetup(view))
        view.tracerViewSelector.triggered.connect(lambda: _showTracerSetup(view))
        view.actionConfigure_Models.triggered.connect(lambda: _openModelDialog(view))
        view.actionExport.triggered.connect(lambda: _exportLightCurves(view))
        view.recordSignal.connect(lambda: _recordWindow(view))
        __boundWindows.append(view)

def _playPauseToggle(window):
    flag = True
    for window in __boundWindows:
        if window.isAnimating:
            flag = False
    if flag:
        cvs = modelControllers()
        dataViews = canvasViews()
        window.isAnimating = True
        for controllerView in cvs:
            parameters = controllerView.buildObject()
            if parameters:
                Model.updateModel(controllerView.modelID, parameters)
            controller = ControllerFactory(dataViews, __UISignals.playSignal, __UISignals.pauseSignal, __UISignals.resetSignal, __UISignals.recordSignal)
            __UISignals.playSignal.emit()
    else:
        window.isAnimating = False
        __UISignals.pauseSignal.emit()
        __UISignals.deactivateSignal.emit()

def _resetHelper(window):
    for window in __boundWindows:
        window.isAnimating = False
    __UISignals.resetSignal.emit()
    for id, model in Model.items():
        model.reset()

def _addCurvePane(window):
        plCanvas = LightCurvePlotView()
        window.addView(plCanvas)

def _addImgPane(window):
        view = LensedImageView()
        controller = factory.LensedImageControllerFactory(view)
        window.addView(view)
        view.sigDestroyed.connect(_destroyController)
        __controllers.append(controller)

def _addMagPane(window):
        view = MagMapView()
        controller = factory.MagMapControllerFactory(view)
        window.addView(view)
        view.sigDestroyed.connect(_destroyController)
        __controllers.append(controller)

def _addParametersPane(window):
        view = ParametersView()
        controller = factory.ParametersControllerFactory(view)
        window.addView(view)
        view.sigDestroyed.connect(_destroyController)
        __controllers.append(controller)

def _addTablePane(window):
    tv = TableView()
    # pc = window.
    pc = _findControllerHelper(ParametersController)
    tableViewController = factory.TableControllerFactory(tv, pc)
    window.addView(tv)
    view.sigDestroyed.connect(_destroyController)
    __controllers.append(tableViewController)

def _toggleRecording(window):
        pass

def _showVisSetup(window):
        window.layout.clear()
        _addCurvePane(window)
        _addImgPane(window)
        _addParametersPane(window)

def _showTableSetup(window):
        window.layout.clear()
        _addParametersPane(window)
        _addTablePane(window)

def _showTracerSetup(window):
        window.layout.clear()
        _addCurvePane(window)
        _addMagPane(window)
        
def _openModelDialog(window):
    dialog = ModelDialog(canvasViews() + [i.view for i in modelControllers()], window)
    dialog.show()
    dialog.accepted.connect(lambda: _configureControllers(dialog.exportModel()))

def _configureControllers(models):
    for id, model in models.items():
        relevantControllers = filter(lambda x: x.modelID == id, modelControllers())
        for i in relevantControllers:
            i.bindFields(model.parameters)
        # if isinstance(model,MagnificationMapModel):
        #     for i in canvasViews():
        #         if isinstance(i,MagMapView):
        #             i.setMagMap(model.magMapArray)

def _exportLightCurves(window):
        pass

def _recordWindow(window):
        pass




def _findController(modelID,controllerType):
    ret = []
    for c in modelControllers():
        if isinstance(c,controllerType) and c.modelID == modelID:
            ret.append(c)
    return ret

def _findView(modelID,windowType):
    ret = []
    for v in views():
        if isinstance(v,windowType) and v.modelID == modelID:
            ret.append(v)
    return ret

def _destroyController(view):
    controller = None
    for c in modelControllers():
        if c.view == view:
            controller = c
    if controller:
        modelControllers().remove(controller)

def _findControllerHelper(kind):
    ret = []
    for c in modelControllers():
        if isinstance(c, kind):
            ret.append(c)
    if len(ret) == 1:
        ret = ret[0]
    elif len(ret) == 0:
        ret = []
    else:
        model = QInputDialog.getItem(None, "Select Model",
            "Please Select a Model to save.",
            map(lambda i: i.modelID, filter(lambda v: isinstance(v, kind), modelControllers())))
        if model[1]:
            ret = next(filter(lambda i:i.modelID == model[0], modelControllers()))
        else:
            ret = []
    return ret

