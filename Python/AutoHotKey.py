import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, QObject, QTimer, QTime
import pyautogui
from pynput import keyboard

form_class = uic.loadUiType("D:/Git/Personal/Python/AutoKey.ui")[0]
# form_class = uic.loadUiType("E:/Git/Personal/Python/AutoKey.ui")[0]
form_class2 = uic.loadUiType("D:/Git/Personal/Python/InputKey.ui")[0]
# form_class2 = uic.loadUiType("E:/Git/Personal/Python/InputKey.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        
        self.specialKey = {16777216: 'esc', 16777252: 'capslock', 16777248: 'shift',
                           16777249: 'ctrl', 16777250: 'win', 16777251: 'alt', 16777217: 'tab',
                           16777234: 'left', 16777235: 'up', 16777236: 'right', 16777237: 'down'}
        
        self.status_run = False
        self.key = ""
        self.cycle = 0
        
        # =============================================================================================================
        
        self.win2 = WindowClass2()
        self.win2.setWindowTitle(' ')
        self.win2.setFixedSize(QSize(150, 100))
        self.win2.setWindowFlags(Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # =============================================================================================================
        
        self.Thread_HotCorner = Thread(self)
        self.Thread_HotCorner.start()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('E:/Git/Personal/Python/AutoIcon-removebg-preview.png'))
        self.setWindowTitle('AutoHotKey')
        self.setFixedSize(QSize(295, 380))
        
        # =============================================================================================================
        
        self.pushButton_Start.clicked.connect(self.ClickedPushButton)
        self.pushButton_Stop.clicked.connect(self.CLickedStopButton)
        self.pushButton_hotkey_1_0.clicked.connect(lambda: self.TTT(0, 0))
        self.pushButton_hotkey_1_1.clicked.connect(lambda: self.TTT(0, 1))
        self.pushButton_hotkey_1_2.clicked.connect(lambda: self.TTT(0, 2))
        self.pushButton_hotkey_2_0.clicked.connect(lambda: self.TTT(1, 0))
        self.pushButton_hotkey_2_1.clicked.connect(lambda: self.TTT(1, 1))
        self.pushButton_hotkey_2_2.clicked.connect(lambda: self.TTT(1, 2))
        self.pushButton_hotkey_3_0.clicked.connect(lambda: self.TTT(2, 0))
        self.pushButton_hotkey_3_1.clicked.connect(lambda: self.TTT(2, 1))
        self.pushButton_hotkey_3_2.clicked.connect(lambda: self.TTT(2, 2))
        self.pushButton_hotkey_4_0.clicked.connect(lambda: self.TTT(3, 0))
        self.pushButton_hotkey_4_1.clicked.connect(lambda: self.TTT(3, 1))
        self.pushButton_hotkey_4_2.clicked.connect(lambda: self.TTT(3, 2))
        
        self.hotKeyList = [[self.pushButton_hotkey_1_0, self.pushButton_hotkey_1_1, self.pushButton_hotkey_1_2],
                           [self.pushButton_hotkey_2_0, self.pushButton_hotkey_2_1, self.pushButton_hotkey_2_2],
                           [self.pushButton_hotkey_3_0, self.pushButton_hotkey_3_1, self.pushButton_hotkey_3_2],
                           [self.pushButton_hotkey_4_0, self.pushButton_hotkey_4_1, self.pushButton_hotkey_4_2]]
        
        # =============================================================================================================
        
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
    
    def TTT(self, hotNum, keyNum):
        if self.win2.isVisible() == False:
            self.win2.SetTargetInfo(hotNum, keyNum)
            self.win2.show()
    
    def SetInputValue(self, value, hotNum, keyNum):
        print('1-1', value, hotNum, keyNum)
        if value < 999:
            self.hotKeyList[hotNum][keyNum].setText(chr(value))
        elif value == 99999999:
            self.hotKeyList[hotNum][keyNum].setText('None')
        elif value in self.specialKey:
            self.hotKeyList[hotNum][keyNum].setText(self.specialKey[value])
    
    def HotKeyAction(self, hotKeyNum):
        if hotKeyNum == 0:
            key1 = self.hotKeyList[0][0].text()
            key2 = self.hotKeyList[0][1].text()
            key3 = self.hotKeyList[0][2].text()
        elif hotKeyNum == 1:
            key1 = self.hotKeyList[1][0].text()
            key2 = self.hotKeyList[1][1].text()
            key3 = self.hotKeyList[1][2].text()
        elif hotKeyNum == 2:
            key1 = self.hotKeyList[2][0].text()
            key2 = self.hotKeyList[2][1].text()
            key3 = self.hotKeyList[2][2].text()
        elif hotKeyNum == 3:
            key1 = self.hotKeyList[3][0].text()
            key2 = self.hotKeyList[3][1].text()
            key3 = self.hotKeyList[3][2].text()
        
        if key1 != "none":
            pyautogui.keyDown(key1)
        if key2 != "none":
            pyautogui.keyDown(key2)
        if key3 != "none":
            pyautogui.keyDown(key3)
        
        if key1 != "none":
            pyautogui.keyUp(key1)
        if key2 != "none":
            pyautogui.keyUp(key2)
        if key3 != "none":
            pyautogui.keyUp(key3)
        
        return

class WindowClass2(QMainWindow, form_class2):
    def __init__(self):
        super().__init__()
    
        self.label_inputkey_title = QLabel(self)
        self.label_inputkey_title.setGeometry(20, 0, 100, 50)
        self.label_inputkey_title.setText('키를 입력하세요')
        self.label_inputkey_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.Button_none = QPushButton(self)
        self.Button_none.setGeometry(50, 50, 50, 25)
        self.Button_none.setText('None')
    
        self.hotNum = 0
        self.keyNum = 0
        self.inputASCII = 0
        
        self.Button_none.clicked.connect(lambda: self.SendInputValue(99999999))
    
    def keyPressEvent(self, e):
        str
        self.inputASCII = int(e.key())

        self.SendInputValue()
    
    def SetTargetInfo(self, hotNum, keyNum):
        self.hotNum = hotNum
        self.keyNum = keyNum
    
    def SendInputValue(self, noneValue = 0):
        if noneValue == 99999999:
            self.inputASCII = 99999999
            
        myWindow.SetInputValue(self.inputASCII, self.hotNum, self.keyNum)
        self.close()

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
            
            # print(self.rect.width(), self.rect.height())
            print(self.curX, self.curY)

            if ((self.curX != self.zero and self.curX != self.width) or (self.curY != self.zero and self.curY != self.height)):
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

    # 1
    def CurPosLeftTop(self):
        myWindow.HotKeyAction(0)
        
    # 2
    def CurPosRightTop(self):
        myWindow.HotKeyAction(1)

    # 3
    def CurPosLeftBottom(self):
        myWindow.HotKeyAction(2)
    
    # 4
    def CurPosRightBottom(self):
        myWindow.HotKeyAction(3)


if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()