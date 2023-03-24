import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from PyQt5 import uic
from PyQt5 import QtGui
import pyautogui

form_class = uic.loadUiType("E:/Git/Personal/Python/AutoKey.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('E:/0_Git/Personal/Python/AutoIcon-removebg-preview.png'))
        self.setWindowTitle('AutoHotKey')
        self.setFixedSize(QSize(295, 195))
        
        self.pushButton_Start.clicked.connect(self.ClickedPushButton)
        self.pushButton_Stop.clicked.connect(self.CLickedStopButton)
        
        self.status_run = False
        self.key = ""
        self.cycle = 0
        
        self.trayIcon = QSystemTrayIcon(QtGui.QIcon('E:/0_Git/Personal/Python/AutoIcon-removebg-preview.png'), app)
        self.trayIcon.setToolTip("상태 : Stop")
        self.TrayInit()        

        pyautogui.FAILSAFE = False
    
    def TrayInit(self):
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        self.trayIcon.setContextMenu(tray_menu)
        
        self.trayIcon.show()
    
    def closeEvent(self, event):
        self.trayIcon.hide()
        sys.exit()
        
    def ClickedPushButton(self):
        if self.status_run == True:
            self.reply = QMessageBox.information(self, 'Message', '이미 실행중입니다')
            return
        
        self.key = self.comboBox_SelectKey.currentText()
        temp = self.lineEdit_Cycle.text()
        
        try:
            self.cycle = int(temp)
        except:
            self.reply = QMessageBox.warning(self, 'Message', '숫자만 입력하세요')
            self.lineEdit_Cycle.clear()
            return
            
        if self.cycle == 0:
            self.reply = QMessageBox.information(self, 'Message', '0보다 큰 숫자를 입력하세요')
            self.lineEdit_Cycle.clear()
        else:
            self.AutoKeyStart()

    def AutoKeyStart(self):        
        self.cycle *= 60000
        self.comboBox_SelectKey.setEnabled(False)
        self.lineEdit_Cycle.setEnabled(False)
        self.status_run = True
        self.trayIcon.setToolTip("상태 : Run")
        self.label_Status.setText("상태 : Run")
        
        while self.status_run:
            pyautogui.keyDown(self.key)
            pyautogui.keyUp(self.key)
            QTest.qWait(100)
            pyautogui.keyDown(self.key)
            pyautogui.keyUp(self.key)
            QTest.qWait(self.cycle)
            
    def CLickedStopButton(self):
        self.comboBox_SelectKey.setEnabled(True)
        self.lineEdit_Cycle.setEnabled(True)
        self.status_run = False
        self.trayIcon.setToolTip("상태 : Stop")
        self.label_Status.setText("상태 : Stop")


if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()