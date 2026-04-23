import maya.cmds as mc 
from PySide6. QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Qt
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance


def GetMayaMainWindow()->QMainWindow:
    GetMayaMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(int(GetMayaMainWindow), QMainWindow)

def RemoveWidgetName(objectName):
    for widget in GetMayaMainWindow().findChildren(QWidget, objectName):
        widget.deleteLater()

class MayaWidget(QWidget):
    def __init__(self):
        super().__init__(parent=GetMayaMainWindow())
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Maya Widget")
        RemoveWidgetName(self.GetWidgetHash())
        self.setObjectName(self.GetWidgetHash())

    def GetWidgetHash(self):
        return "da36370ba3acceb0751bb0875af55932c76e1a35e3bb1568d9c37adb1f922979"
