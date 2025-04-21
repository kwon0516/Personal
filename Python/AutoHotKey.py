import os
import sys
import pyautogui
import configparser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import QEvent

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

form = resource_path(BASE_DIR + "\AutoKey.ui")
form_class = uic.loadUiType(form)[0]
form2 = resource_path(BASE_DIR + "\InputKey.ui")
form_class2 = uic.loadUiType(form)[0]


# form_class = uic.loadUiType("D:/Git/Personal/Python/AutoKey.ui")[0]
# # form_class = uic.loadUiType("E:/Git/Personal/Python/AutoKey.ui")[0]
# form_class2 = uic.loadUiType("D:/Git/Personal/Python/InputKey.ui")[0]
# # form_class2 = uic.loadUiType("E:/Git/Personal/Python/InputKey.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        
        self.specialKey = {16777216: 'esc', 16777252: 'capslock', 16777248: 'shift',
                           16777249: 'ctrl', 16777250: 'win', 16777251: 'alt', 16777217: 'tab',
                           16777234: 'left', 16777235: 'up', 16777236: 'right', 16777237: 'down',
                           16777264: 'f1', 16777265: 'f2', 16777266: 'f3', 16777267: 'f4', 16777268: 'f5',
                           16777269: 'f6', 16777270: 'f7', 16777271: 'f8', 16777272: 'f9', 16777273: 'f10',
                           16777274: 'f11', 16777275: 'f12'}
        
        self.status_run = False
        self.key = ""
        self.cycle = 0
        
        self.useMonitor1 = False
        self.useMonitor2 = False
        
        # =============================================================================================================
        
        self.win2 = WindowClass2()
        self.win2.setWindowTitle(' ')
        self.win2.setFixedSize(QSize(150, 100))
        self.win2.setWindowFlags(Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # =============================================================================================================
        
        self.Thread_HotCorner = Thread(self)
        # self.Thread_HotCorner.start()
        self.setupUi(self)
        # self.setWindowIcon(QtGui.QIcon('D:/Git/Personal/Python/AutoIcon-removebg-preview.png'))
        self.setWindowIcon(QtGui.QIcon('E:/Git/Personal/Python/AutoIcon-removebg-preview.png'))
        self.setWindowTitle('AutoHotKey')
        self.setFixedSize(QSize(295, 600))
        
        # =============================================================================================================
        
        self.pushButton_Start.clicked.connect(self.ClickedPushButton)
        self.pushButton_Stop.clicked.connect(self.CLickedStopButton)
        
        self.pushButton_hotkey_0_0.clicked.connect(lambda: self.SetButtonText(0, 0))
        self.pushButton_hotkey_0_1.clicked.connect(lambda: self.SetButtonText(0, 1))
        self.pushButton_hotkey_0_2.clicked.connect(lambda: self.SetButtonText(0, 2))
        self.pushButton_hotkey_1_0.clicked.connect(lambda: self.SetButtonText(1, 0))
        self.pushButton_hotkey_1_1.clicked.connect(lambda: self.SetButtonText(1, 1))
        self.pushButton_hotkey_1_2.clicked.connect(lambda: self.SetButtonText(1, 2))
        self.pushButton_hotkey_2_0.clicked.connect(lambda: self.SetButtonText(2, 0))
        self.pushButton_hotkey_2_1.clicked.connect(lambda: self.SetButtonText(2, 1))
        self.pushButton_hotkey_2_2.clicked.connect(lambda: self.SetButtonText(2, 2))
        self.pushButton_hotkey_3_0.clicked.connect(lambda: self.SetButtonText(3, 0))
        self.pushButton_hotkey_3_1.clicked.connect(lambda: self.SetButtonText(3, 1))
        self.pushButton_hotkey_3_2.clicked.connect(lambda: self.SetButtonText(3, 2))
        
        self.pushButton_Calibration_LeftTop_1.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 0, 0))
        self.pushButton_Calibration_RightTop_1.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 0, 1))
        self.pushButton_Calibration_LeftBottom_1.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 0, 2))
        self.pushButton_Calibration_RightBottom_1.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 0, 3))
        self.pushButton_Calibration_LeftTop_2.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 1, 0))
        self.pushButton_Calibration_RightTop_2.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 1, 1))
        self.pushButton_Calibration_LeftBottom_2.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 1, 2))
        self.pushButton_Calibration_RightBottom_2.clicked.connect(lambda: self.SetButtonText(0, 0, 1, 1, 3))
        
        self.pushButton_Save.clicked.connect(self.SavePreference)
        self.pushButton_Exit.clicked.connect(self.closeEvent)
        
        self.hotKeyList = [[self.pushButton_hotkey_0_0, self.pushButton_hotkey_0_1, self.pushButton_hotkey_0_2],
                           [self.pushButton_hotkey_1_0, self.pushButton_hotkey_1_1, self.pushButton_hotkey_1_2],
                           [self.pushButton_hotkey_2_0, self.pushButton_hotkey_2_1, self.pushButton_hotkey_2_2],
                           [self.pushButton_hotkey_3_0, self.pushButton_hotkey_3_1, self.pushButton_hotkey_3_2]]
        
        self.CalibrationValueList = [[self.pushButton_Calibration_LeftTop_1, self.pushButton_Calibration_RightTop_1,
                                      self.pushButton_Calibration_LeftBottom_1, self.pushButton_Calibration_RightBottom_1],
                                     [self.pushButton_Calibration_LeftTop_2, self.pushButton_Calibration_RightTop_2,
                                      self.pushButton_Calibration_LeftBottom_2, self.pushButton_Calibration_RightBottom_2]]
        
        self.value0_0_x = 0
        self.value0_0_y = 0
        self.value0_1_x = 0
        self.value0_1_y = 0
        self.value0_2_x = 0
        self.value0_2_y = 0
        self.value0_3_x = 0
        self.value0_3_y = 0
        self.value1_0_x = 0
        self.value1_0_y = 0
        self.value1_1_x = 0
        self.value1_1_y = 0
        self.value1_2_x = 0
        self.value1_2_y = 0
        self.value1_3_x = 0
        self.value1_3_y = 0
        
        self.calibrationValue = [[self.value0_0_x, self.value0_0_y], [self.value0_1_x, self.value0_1_y], [self.value0_2_x, self.value0_2_y], [self.value0_3_x, self.value0_3_y],
                                 [self.value1_0_x, self.value1_0_y], [self.value1_1_x, self.value1_1_y], [self.value1_2_x, self.value1_2_y], [self.value1_3_x, self.value1_3_y]]
        
        # =============================================================================================================
        
        # self.trayIcon = QSystemTrayIcon(QtGui.QIcon('D:/Git/Personal/Python/AutoIcon-removebg-preview.png'), app)
        self.trayIcon = QSystemTrayIcon(QtGui.QIcon('E:/Git/Personal/Python/AutoIcon-removebg-preview.png'), app)
        self.trayIcon.setToolTip("상태 : Stop")
        self.TrayInit()

        pyautogui.FAILSAFE = False
        
        self.InitPreference()
        
        self.Thread_HotCorner.start()
        
        # ================ 프로그램 실행 시 자동 시작 ================ #
        # self.key = self.key = self.comboBox_SelectKey.currentText()
        # self.cycle = int(self.lineEdit_Cycle.text())
        
        # self.timer = QTimer(self)
        # self.timer.start(1500)
        # self.timer.timeout.connect(self.AutoKeyStart)
        # ================ 프로그램 실행 시 자동 시작 ================ #
    
    def InitPreference(self):
        config = configparser.ConfigParser()
        # path = os.path.dirname(os.path.abspath(__file__)) 
        # path += '\config.ini'
        path = 'D:\AutoHotKey\config.ini'
        readSuccess = config.read(path)

        if len(readSuccess) == 0:
            self.CreatePreference()
        else:
            self.comboBox_SelectKey.setCurrentIndex(int(config['AutoHotKey']['Key']))
            self.lineEdit_Cycle.setText(config['AutoHotKey']['Cycle'])
            
            self.pushButton_hotkey_0_0.setText(config['HotCorner']['0_0'])
            self.pushButton_hotkey_0_1.setText(config['HotCorner']['0_1'])
            self.pushButton_hotkey_0_2.setText(config['HotCorner']['0_2'])
            
            self.pushButton_hotkey_1_0.setText(config['HotCorner']['1_0'])
            self.pushButton_hotkey_1_1.setText(config['HotCorner']['1_1'])
            self.pushButton_hotkey_1_2.setText(config['HotCorner']['1_2'])
            
            self.pushButton_hotkey_2_0.setText(config['HotCorner']['2_0'])
            self.pushButton_hotkey_2_1.setText(config['HotCorner']['2_1'])
            self.pushButton_hotkey_2_2.setText(config['HotCorner']['2_2'])
            
            self.pushButton_hotkey_3_0.setText(config['HotCorner']['3_0'])
            self.pushButton_hotkey_3_1.setText(config['HotCorner']['3_1'])
            self.pushButton_hotkey_3_2.setText(config['HotCorner']['3_2'])
            
            self.pushButton_Calibration_LeftTop_1.setText(config['Calibration']['0_0'])
            self.pushButton_Calibration_RightTop_1.setText(config['Calibration']['0_1'])
            self.pushButton_Calibration_LeftBottom_1.setText(config['Calibration']['0_2'])
            self.pushButton_Calibration_RightBottom_1.setText(config['Calibration']['0_3'])
            
            self.pushButton_Calibration_LeftTop_2.setText(config['Calibration']['1_0'])
            self.pushButton_Calibration_RightTop_2.setText(config['Calibration']['1_1'])
            self.pushButton_Calibration_LeftBottom_2.setText(config['Calibration']['1_2'])
            self.pushButton_Calibration_RightBottom_2.setText(config['Calibration']['1_3'])

            use = False if config['UseMonitor']['0'] == '0' else True
            self.useMonitor1 = use
            self.checkBox_Monitor_1.setChecked(use)
            use = False if config['UseMonitor']['1'] == '0' else True
            self.useMonitor2 = use
            self.checkBox_Monitor_2.setChecked(use)
            # self.checkBox_Monitor_1.setChecked(False if config['UseMonitor']['0'] == '0' else True)
            # self.checkBox_Monitor_2.setChecked(False if config['UseMonitor']['1'] == '0' else True)
            
            self.calibrationValue[0][0] = config['Calibration']['0_0'].split('.')[0]
            self.calibrationValue[0][1] = config['Calibration']['0_0'].split('.')[1]
            self.calibrationValue[1][0] = config['Calibration']['0_1'].split('.')[0]
            self.calibrationValue[1][1] = config['Calibration']['0_1'].split('.')[1]
            self.calibrationValue[2][0] = config['Calibration']['0_2'].split('.')[0]
            self.calibrationValue[2][1] = config['Calibration']['0_2'].split('.')[1]
            self.calibrationValue[3][0] = config['Calibration']['0_3'].split('.')[0]
            self.calibrationValue[3][1] = config['Calibration']['0_3'].split('.')[1]
            
            self.calibrationValue[4][0] = config['Calibration']['1_0'].split('.')[0]
            self.calibrationValue[4][1] = config['Calibration']['1_0'].split('.')[1]
            self.calibrationValue[5][0] = config['Calibration']['1_1'].split('.')[0]
            self.calibrationValue[5][1] = config['Calibration']['1_1'].split('.')[1]
            self.calibrationValue[6][0] = config['Calibration']['1_2'].split('.')[0]
            self.calibrationValue[6][1] = config['Calibration']['1_2'].split('.')[1]
            self.calibrationValue[7][0] = config['Calibration']['1_3'].split('.')[0]
            self.calibrationValue[7][1] = config['Calibration']['1_3'].split('.')[1]
            
            # self.value0_0_x = config['Calibration']['0_0'].split('.')[0]
            # self.value0_0_y = config['Calibration']['0_0'].split('.')[1]
            # self.value0_1_x = config['Calibration']['0_1'].split('.')[0]
            # self.value0_1_y = config['Calibration']['0_1'].split('.')[1]
            # self.value0_2_x = config['Calibration']['0_2'].split('.')[0]
            # self.value0_2_y = config['Calibration']['0_2'].split('.')[1]
            # self.value0_3_x = config['Calibration']['0_3'].split('.')[0]
            # self.value0_3_y = config['Calibration']['0_3'].split('.')[1]
            
            # self.value1_0_x = config['Calibration']['1_0'].split('.')[0]
            # self.value1_0_y = config['Calibration']['1_0'].split('.')[1]
            # self.value1_1_x = config['Calibration']['1_1'].split('.')[0]
            # self.value1_1_y = config['Calibration']['1_1'].split('.')[1]
            # self.value1_2_x = config['Calibration']['1_2'].split('.')[0]
            # self.value1_2_y = config['Calibration']['1_2'].split('.')[1]
            # self.value1_3_x = config['Calibration']['1_3'].split('.')[0]
            # self.value1_3_y = config['Calibration']['1_3'].split('.')[1]
            
            self.Thread_HotCorner.SetCalibrationValue(self.calibrationValue)
            
    def CreatePreference(self):
        config = configparser.ConfigParser()
        # path = os.path.dirname(os.path.abspath(__file__))
        # path += '\config.ini'
        path = 'D:\AutoHotKey\config.ini'

        config['AutoHotKey'] = {}
        config['AutoHotKey']['Key'] = '0'
        config['AutoHotKey']['Cycle'] = '1'

        config['HotCorner'] = {}
        config['HotCorner']['0_0'] = 'none'
        config['HotCorner']['0_1'] = 'none'
        config['HotCorner']['0_2'] = 'none'
        
        config['HotCorner']['1_0'] = 'none'
        config['HotCorner']['1_1'] = 'none'
        config['HotCorner']['1_2'] = 'none'
        
        config['HotCorner']['2_0'] = 'none'
        config['HotCorner']['2_1'] = 'none'
        config['HotCorner']['2_2'] = 'none'
        
        config['HotCorner']['3_0'] = 'none'
        config['HotCorner']['3_1'] = 'none'
        config['HotCorner']['3_2'] = 'none'
        
        config['Calibration'] = {}
        config['Calibration']['0_0'] = '0.0'
        config['Calibration']['0_1'] = '0.0'
        config['Calibration']['0_2'] = '0.0'
        config['Calibration']['0_3'] = '0.0'
        
        config['Calibration']['1_0'] = '0.0'
        config['Calibration']['1_1'] = '0.0'
        config['Calibration']['1_2'] = '0.0'
        config['Calibration']['1_3'] = '0.0'
        
        config['UseMonitor'] = {}
        config['UseMonitor']['0'] = '0'
        config['UseMonitor']['1'] = '0'

        if os.path.exists('D:\AutoHotKey') == False:
            os.mkdir('D:\AutoHotKey')
        
        with open(path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def SavePreference(self):
        config = configparser.ConfigParser()
        # path = os.path.dirname(os.path.abspath(__file__)) 
        # path += '\config.ini'
        path = 'D:\AutoHotKey\config.ini'
        readSuccess = config.read(path)

        if len(readSuccess) == 0:
            self.CreatePreference()
            self.SavePreference()
        else:
            config['AutoHotKey']['Key'] = str(self.comboBox_SelectKey.currentIndex())
            config['AutoHotKey']['Cycle'] = self.lineEdit_Cycle.text()

            config['HotCorner']['0_0'] = self.pushButton_hotkey_0_0.text()
            config['HotCorner']['0_1'] = self.pushButton_hotkey_0_1.text()
            config['HotCorner']['0_2'] = self.pushButton_hotkey_0_2.text()
            
            config['HotCorner']['1_0'] = self.pushButton_hotkey_1_0.text()
            config['HotCorner']['1_1'] = self.pushButton_hotkey_1_1.text()
            config['HotCorner']['1_2'] = self.pushButton_hotkey_1_2.text()
            
            config['HotCorner']['2_0'] = self.pushButton_hotkey_2_0.text()
            config['HotCorner']['2_1'] = self.pushButton_hotkey_2_1.text()
            config['HotCorner']['2_2'] = self.pushButton_hotkey_2_2.text()
            
            config['HotCorner']['3_0'] = self.pushButton_hotkey_3_0.text()
            config['HotCorner']['3_1'] = self.pushButton_hotkey_3_1.text()
            config['HotCorner']['3_2'] = self.pushButton_hotkey_3_2.text()
            
            config['Calibration']['0_0'] = self.pushButton_Calibration_LeftTop_1.text()
            config['Calibration']['0_1'] = self.pushButton_Calibration_RightTop_1.text()
            config['Calibration']['0_2'] = self.pushButton_Calibration_LeftBottom_1.text()
            config['Calibration']['0_3'] = self.pushButton_Calibration_RightBottom_1.text()
            
            config['Calibration']['1_0'] = self.pushButton_Calibration_LeftTop_2.text()
            config['Calibration']['1_1'] = self.pushButton_Calibration_RightTop_2.text()
            config['Calibration']['1_2'] = self.pushButton_Calibration_LeftBottom_2.text()
            config['Calibration']['1_3'] = self.pushButton_Calibration_RightBottom_2.text()
            
            config['UseMonitor']['0'] = '0' if self.checkBox_Monitor_1.isChecked() == False else '1'
            config['UseMonitor']['1'] = '0' if self.checkBox_Monitor_2.isChecked() == False else '1'
            
            with open(path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        
        self.InitPreference()
    
    def IsUseMonitor(self, monitorNum):
        if monitorNum == 0:
            return self.useMonitor1
        else:
            return self.useMonitor2
    
    def GetCalibrationValue(self):
        return self.calibrationValue
    
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
            self.raise_()
            self.activateWindow()

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
            pyautogui.press(self.key)
            pyautogui.press(self.key)
            QTest.qWait(self.cycle)
            
            # keyDown은 딜레이가 너무 길어서 press로 변경
            # pyautogui.keyDown(self.key)
            # pyautogui.keyUp(self.key)
            # QTest.qWait(100)
            # pyautogui.keyDown(self.key)
            # pyautogui.keyUp(self.key)
            # QTest.qWait(self.cycle)
            
    def CLickedStopButton(self):
        self.comboBox_SelectKey.setEnabled(True)
        self.lineEdit_Cycle.setEnabled(True)
        self.status_run = False
        self.trayIcon.setToolTip("상태 : Stop")
        self.label_Status.setText("상태 : Stop")
    
    def SetButtonText(self, hotNum, keyNum, mode = 0, monitorNum = 0, calibrationPosition = 0):
        if self.win2.isVisible() == False:
            if mode == 0:
                self.win2.SetMode(0)
            else:
                self.win2.SetMode(1, monitorNum, calibrationPosition)
                
            self.win2.SetTargetInfo(hotNum, keyNum)
            self.win2.show()
    
    def SetInputValue(self, value, hotNum, keyNum):
        if value < 999:
            self.hotKeyList[hotNum][keyNum].setText(chr(value))
        elif value == 99999999:
            self.hotKeyList[hotNum][keyNum].setText('None')
        elif value in self.specialKey:
            self.hotKeyList[hotNum][keyNum].setText(self.specialKey[value])
    
    def SetCalibrationValue(self, x, y, monitorNum, calibrationPosition):
        text = "{}.{}".format(x, y)
        self.CalibrationValueList[monitorNum][calibrationPosition].setText(text)
    
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
        
        keys = [key1, key2, key3]
        keys = [k.lower() for k in keys if k.lower() != "none"]

        if keys:
            # 조합 키를 순서대로 누르기
            for k in keys[:-1]:
                pyautogui.keyDown(k)
            pyautogui.press(keys[-1])  # 마지막 키는 press로
            for k in reversed(keys[:-1]):
                pyautogui.keyUp(k)
        #     print("HotKeyAction 실행됨:", keys)
        # else:
        #     print("HotKeyAction: 등록된 키 없음 (모두 none)")

        # ======================================================== #
        
        # Ctrl + L 같은 조합키가 동작 안하는 경우에 대응 및 none 예외처리 추가로 위 방식으로 변경 [2차 버전]
        # pyautogui.hotkey(key1, key2, key3, interval = 0.05)
        # print(key1, key2, key3);

        # ======================================================== #

        # keyDown은 딜레이가 너무 길어서 hotkey로 변경 [1차 버전]
        # if key1 != "none":
        #     pyautogui.keyDown(key1)
        # if key2 != "none":
        #     pyautogui.keyDown(key2)
        # if key3 != "none":
        #     pyautogui.keyDown(key3)
        
        # if key1 != "none":
        #     pyautogui.keyUp(key1)
        # if key2 != "none":
        #     pyautogui.keyUp(key2)
        # if key3 != "none":
        #     pyautogui.keyUp(key3)

        # ======================================================== #
    
    def GetCurMousePosition(self):
        curX, curY = self.Thread_HotCorner.GetCurMousePosition()

        return [curX, curY]

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
        
        self.mode = 0 # 0 = 핫코너, 1 = 좌표 보정
        self.monitorNum = 0
        self.calibrationPosition = 0
        
        self.Button_none.clicked.connect(lambda: self.SendInputValue(99999999))
    
    def SetMode(self, mode, monitorNum = 0, calibrationPosition = 0):
        if mode == 0:
            self.mode = 0
            self.label_inputkey_title.setText('키를 입력하세요')
            self.Button_none.show()
        else:
            self.mode = 1
            self.monitorNum = monitorNum
            self.calibrationPosition = calibrationPosition
            self.label_inputkey_title.setText('좌표에서 Enter')
            self.Button_none.hide()
        
        self.mode = mode
    
    def keyPressEvent(self, e):
        self.inputASCII = int(e.key())
        
        if self.mode == 0:
            self.SendInputValue()
        elif self.mode == 1 and self.inputASCII == 16777220: # 16777220 : Enter
            curX, curY = myWindow.GetCurMousePosition()
            self.SendCalibrationValue(curX, curY)
    
    def SetTargetInfo(self, hotNum, keyNum):
        self.hotNum = hotNum
        self.keyNum = keyNum
    
    def SendInputValue(self, noneValue = 0):
        if noneValue == 99999999:
            self.inputASCII = 99999999
            
        myWindow.SetInputValue(self.inputASCII, self.hotNum, self.keyNum)
        self.close()
    
    def SendCalibrationValue(self, x, y):
        myWindow.SetCalibrationValue(x, y, self.monitorNum, self.calibrationPosition)
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
        self.calibrationValue = []
        
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
            
            self.curX = str(pyautogui.position().x)
            self.curY = str(pyautogui.position().y)
            
            if (myWindow.IsUseMonitor(0) and self.curX == self.calibrationValue[0][0] and self.curY == self.calibrationValue[0][1]) or (myWindow.IsUseMonitor(1) and self.curX == self.calibrationValue[4][0] and self.curY == self.calibrationValue[4][1]):
                if self.actionFlag: self.CurPosLeftTop()
            elif (myWindow.IsUseMonitor(0) and self.curX == self.calibrationValue[1][0] and self.curY == self.calibrationValue[1][1]) or (myWindow.IsUseMonitor(1) and self.curX == self.calibrationValue[5][0] and self.curY == self.calibrationValue[5][1]):
                if self.actionFlag: self.CurPosRightTop()
            elif (myWindow.IsUseMonitor(0) and self.curX == self.calibrationValue[2][0] and self.curY == self.calibrationValue[2][1]) or (myWindow.IsUseMonitor(1) and self.curX == self.calibrationValue[6][0] and self.curY == self.calibrationValue[6][1]):
                if self.actionFlag: self.CurPosLeftBottom()
            elif (myWindow.IsUseMonitor(0) and self.curX == self.calibrationValue[3][0] and self.curY == self.calibrationValue[3][1]) or (myWindow.IsUseMonitor(1) and self.curX == self.calibrationValue[7][0] and self.curY == self.calibrationValue[7][1]):
                if self.actionFlag: self.CurPosRightBottom()
            else:
                self.actionFlag = True
                # for i in range(0, 8):
                #     for j in range(0, 2):
                #         if j == 0:
                #             if self.calibrationValue[i][j] != self.curX:
                #                 print(self.calibrationValue[i][j])
                #                 self.actionFlag = True
                #         else:
                #             if self.calibrationValue[i][j] != self.curY:
                #                 print(self.calibrationValue[i][j])
                #                 self.actionFlag = True
                # print("==============")
                
            # if ((self.curX != self.zero and self.curX != self.width) or (self.curY != self.zero and self.curY != self.height)):
            #     self.actionFlag = True
            # elif (self.actionFlag and self.curX == self.zero and self.curY == self.zero):
            #     self.CurPosLeftTop()
            #     self.actionFlag = False
            # elif (self.actionFlag and self.curX >= self.width and self.curY == self.zero):
            #     self.CurPosRightTop()
            #     self.actionFlag = False
            # elif (self.actionFlag and self.curX == self.zero and self.curY >= self.height):
            #     self.CurPosLeftBottom()
            #     self.actionFlag = False
            # elif (self.actionFlag and self.curX >= self.width and self.curY >= self.height):
            #     self.CurPosRightBottom()
            #     self.actionFlag = False
    
    def SetCalibrationValue(self, l):
        self.calibrationValue = l
    
    def GetCurMousePosition(self):
        return [self.curX, self.curY]
    
    def StopThread(self):
        self.ThreadFlag = False

    # 1
    def CurPosLeftTop(self):
        myWindow.HotKeyAction(0)
        self.actionFlag = False
        
    # 2
    def CurPosRightTop(self):
        myWindow.HotKeyAction(1)
        self.actionFlag = False

    # 3
    def CurPosLeftBottom(self):
        myWindow.HotKeyAction(2)
        self.actionFlag = False
    
    # 4
    def CurPosRightBottom(self):
        myWindow.HotKeyAction(3)
        self.actionFlag = False


if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()