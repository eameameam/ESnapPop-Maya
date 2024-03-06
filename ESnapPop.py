import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import os

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class SnapButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(SnapButton, self).__init__(parent)
        self.snap_modes = {
            "Grid Snap": "grid",
            "Curve Snap": "curve",
            "Point Snap": "point",
            "MeshCenter Snap": "meshCenter",
            "Plane Snap": "viewPlane",
        }

    def mousePressEvent(self, event):
        self.parent().check_alt()
        if event.button() == QtCore.Qt.RightButton:
            for button in self.parent().findChildren(SnapButton):
                snap_mode_for_button = self.snap_modes[button.toolTip()]
                cmds.snapMode(**{snap_mode_for_button: False})
                button.setProperty("active", "false")
                button.style().unpolish(button)
                button.style().polish(button)
            cmds.inViewMessage(amg="All Snap Modes Off", pos='topCenter', fade=True)
        elif event.button() == QtCore.Qt.LeftButton:
            self.parent().is_alt_pressed = QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier
            super().mousePressEvent(event)

class ESnapPopWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(ESnapPopWindow, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.setWindowOpacity(0.9)
        self.installEventFilter(self)

        self.frame = QtWidgets.QWidget(self)
        self.frame.setStyleSheet("""
            QWidget {
                background-color: rgba(38, 38, 38, 240);
                border-radius: 10px;
                min-width: 200px;
                min-height: 40px;
            }
        """)

        self.main_layout = QtWidgets.QHBoxLayout(self.frame)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        icon_folder = os.path.join(cmds.internalVar(userPrefDir=True), "icons", "SnapPopIcons")

        self.create_button("Grid Snap", "grid", os.path.join(icon_folder, "snapGrid.png"))
        self.create_button("Curve Snap", "curve", os.path.join(icon_folder, "snapCurve.png"))
        self.create_button("Point Snap", "point", os.path.join(icon_folder, "snapPoint.png"))
        self.create_button("MeshCenter Snap", "meshCenter", os.path.join(icon_folder, "snapMeshCenter.png"))
        self.create_button("Plane Snap", "viewPlane", os.path.join(icon_folder, "snapPlane.png"))

        self.main_layout.setContentsMargins(5, 5, -15, 5)

        self.adjustSize()

        cursor = QtGui.QCursor()
        self.move(cursor.pos() - self.rect().center())

        self.show()

        self.is_pressed = False
        self.is_shift_pressed = False
        self.is_alt_pressed = False

        self.shift_timer = QtCore.QTimer()
        self.shift_timer.timeout.connect(self.check_shift)

        self.alt_timer = QtCore.QTimer()
        self.alt_timer.timeout.connect(self.check_alt)

    def create_button(self, label, snap_mode, icon_path):
        button = SnapButton()
        button.setToolTip(label)

        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 10, 10, 240);
                border-radius: 10px;
                min-width: 0;
                min-height: 0;
            }
            QPushButton::hover {
                background-color: rgba(20, 20, 20, 240);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 240);
            }
            QPushButton[active="true"] {
                background-color: rgba(82, 133, 166, 240);
            }
        """)

        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(30, 30))
        button.setFixedSize(40, 40)

        def toggle_snap_mode():
            if cmds.snapMode(q=True, **{snap_mode: True}):
                if self.is_alt_pressed: 
                    for b in self.findChildren(QtWidgets.QPushButton):
                        if b is not button:
                            snap_mode_for_other_button = b.snap_modes[b.toolTip()]
                            cmds.snapMode(**{snap_mode_for_other_button: False})
                            b.setProperty("active", "false")
                            b.style().unpolish(b)
                            b.style().polish(b)
                    cmds.inViewMessage(amg="Only " + label + " On", pos='topCenter', fade=True)
                else:
                    cmds.inViewMessage(amg=label + " Off", pos='topCenter', fade=True)
                    cmds.snapMode(**{snap_mode: False})
                    button.setProperty("active", "false")
            else:
                cmds.inViewMessage(amg=label + " On", pos='topCenter', fade=True) 
                cmds.snapMode(**{snap_mode: True})
                if self.is_alt_pressed: 
                    for b in self.findChildren(QtWidgets.QPushButton):
                        if b is not button:
                            snap_mode_for_other_button = button.snap_modes[b.toolTip()]
                            cmds.snapMode(**{snap_mode_for_other_button: False})
                            b.setProperty("active", "false")
                            b.style().unpolish(b)
                            b.style().polish(b)
                    cmds.inViewMessage(amg="Only " + label + " On", pos='topCenter', fade=True)
                button.setProperty("active", "true")
            button.style().unpolish(button)
            button.style().polish(button)


        
        button.clicked.connect(toggle_snap_mode)
        button.pressed.connect(self.button_pressed)
        button.released.connect(self.button_released)

        if cmds.snapMode(query=True, **{snap_mode: True}):
            button.setProperty("active", "true")
        else:
            button.setProperty("active", "false")

        button.style().unpolish(button)
        button.style().polish(button)

        self.main_layout.addWidget(button)

    def reset_other_buttons(self, active_button):
        for b in self.findChildren(QtWidgets.QPushButton):
            if b is not active_button:
                snap_mode_for_other_button = b.snap_modes[b.toolTip()]
                cmds.snapMode(**{snap_mode_for_other_button: False})
                b.setProperty("active", "false")
                b.style().unpolish(b)
                b.style().polish(b)

    def button_pressed(self):
        self.is_pressed = True
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            self.is_shift_pressed = True
            self.shift_timer.start(100)
        if modifiers == QtCore.Qt.AltModifier:
            self.is_alt_pressed = True
            self.alt_timer.start(100)

    
    def button_released(self):
        if self.is_pressed and not self.is_shift_pressed:
            self.close()
            self.is_pressed = False
            
    def check_shift(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers != QtCore.Qt.ShiftModifier:
            if self.is_shift_pressed:
                self.close()
            self.is_shift_pressed = False
            self.shift_timer.stop()

    def check_alt(self):
        self.is_alt_pressed = QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier


    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Leave:
            self.close()
        return False
    
def create_popup_window():
    global popup_window
    if popup_window is not None and popup_window.isVisible():
        popup_window.close()
    popup_window = ESnapPopWindow()

popup_window = None

create_popup_window()
