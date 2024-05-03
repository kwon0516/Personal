import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, QObject, QTimer, QTime
import pyautogui
from pynput import keyboard

form_class = uic.loadUiType("E:/Git/Personal/Python/AutoKey.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        
        self.Thread_HotCorner = Thread(self)
        self.Thread_HotCorner.start()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('E:/Git/Personal/Python/AutoIcon-removebg-preview.png'))
        self.setWindowTitle('AutoHotKey')
        self.setFixedSize(QSize(295, 195))
        
        self.pushButton_Start.clicked.connect(self.ClickedPushButton)
        self.pushButton_Stop.clicked.connect(self.CLickedStopButton)
        
        self.status_run = False
        self.key = ""
        self.cycle = 0
        
        self.trayIcon = QSystemTrayIcon(QtGui.QIcon('E:/Git/Personal/Python/AutoIcon-removebg-preview.png'), app)
        self.trayIcon.setToolTip("상태 : Stop")
        self.TrayInit()

        pyautogui.FAILSAFE = False
        
        # ================ 프로그램 실행 시 자동 시작 ================ #
        self.key = self.key = self.comboBox_SelectKey.currentText()
        self.cycle = int(self.lineEdit_Cycle.text())
        
        self.timer = QTimer(self)
        self.timer.start(1500)
        self.timer.timeout.connect(self.AutoKeyStart)
        # ================ 프로그램 실행 시 자동 시작 ================ #
    
    def TrayInit(self):
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        exit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        exit_action.triggered.connect(self.closeEvent)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(exit_action)
        self.trayIcon.setContextMenu(tray_menu)
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.DoubleClickedTrayIcon)
    
    def DoubleClickedTrayIcon(self, reson):
        if (reson == QSystemTrayIcon.DoubleClick):
            self.showNormal()
            # if (self.isVisible()):
            #     self.show()
    
    def changeEvent(self, event):
        if (event.type() == QEvent.WindowStateChange):
            if (self.windowState() & Qt.WindowMinimized):
                self.showMinimized()
                self.hide()
    
    def closeEvent(self, event):
        self.Thread_HotCorner.StopThread()
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
    
    def keyPressEvent(self, e):
        str;
        inputASCII = int(e.key())
        if inputASCII == 16777252:
            print("Capslock")
        
        print(int(e.key()))
        # print(chr(int(e.key())))
        
        # print(type(e.text()))
        print("===========")

    
class Thread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.zero = 0
        self.curX = 9999
        self.curY = 9999
        self.actionFlag = True
        self.ThreadFlag = True
        
        # print(app.desktop().screen(0).screen().name())
        # print(app.screenAt(QPoint(0,0)).name())

        # while문 안으로 이동(듀얼모니터 대응)
        # self.rect = app.desktop().screenGeometry()
        # self.width, self.height = self.rect.width() - 1, self.rect.height() - 1
        # print(self.width, self.height)
        
    def run(self):
        while(self.ThreadFlag):
            self.rect = app.desktop().screenGeometry()
            self.width, self.height = self.rect.width() - 1, self.rect.height() - 1
            
            self.curX = pyautogui.position().x
            self.curY = pyautogui.position().y

            if (self.curX > self.zero and self.curY > self.zero):
                self.actionFlag = True
            elif (self.actionFlag and self.curX == self.zero and self.curY == self.zero):
                self.CurPosLeftTop()
                self.actionFlag = False
            elif (self.actionFlag and self.curX >= self.width and self.curY == self.zero):
                self.CurPosRightTop()
                self.actionFlag = False
            elif (self.actionFlag and self.curX == self.zero and self.curY >= self.height):
                self.CurPosLeftBottom()
                self.actionFlag = False
            elif (self.actionFlag and self.curX >= self.width and self.curY >= self.height):
                self.CurPosRightBottom()
                self.actionFlag = False
    
    def StopThread(self):
        self.ThreadFlag = False

    # Chrome
    def CurPosLeftTop(self):
            pyautogui.keyDown("winleft")
            pyautogui.keyDown("1")
            pyautogui.keyUp("1")
            pyautogui.keyUp("winleft")
        
    # Visual Studio
    def CurPosRightTop(self):
        pyautogui.keyDown("winleft")
        pyautogui.keyDown("2")
        pyautogui.keyUp("2")
        pyautogui.keyUp("winleft")

    # SoruceTree
    def CurPosLeftBottom(self):
            pyautogui.keyDown("winleft")
            pyautogui.keyDown("4")
            pyautogui.keyUp("4")
            pyautogui.keyUp("winleft")
    
    # Go Desktop
    def CurPosRightBottom(self):
        pyautogui.keyDown("winleft")
        pyautogui.keyDown("d")
        pyautogui.keyUp("d")
        pyautogui.keyUp("winleft")


if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()