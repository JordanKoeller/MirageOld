

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QCheckBox, QSpinBox


class PreferencesDialog(QDialog):
    
    def __init__(self,uiFile,parent=None):
        QDialog.__init__(self,parent)
        uic.loadUi(uiFile,self)
    
    def _getSettings(self):
        ret = {}
        for k,v in self.__dict__.items():
            if isinstance(v, QCheckBox):
                ret.update({k:v.isChecked()})
            elif isinstance(v, QSpinBox):
                ret.update({k:v.value()})
        return ret
        
    def exec(self):
        if QDialog.exec(self):
            return self._getSettings()
        else:
            return None