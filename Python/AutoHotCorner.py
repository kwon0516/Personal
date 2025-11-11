# -*- coding: utf-8 -*-
"""
AutoHotCorner (PyQt5, single-file)
- No .ui files needed (UI fully in code)
- Non-blocking timers (no while-loops that freeze UI)
- System tray controls, nicer styling, friendlier messages
- Config saved in %APPDATA%\AutoHotCorner\config.json (Windows) or ~/.config/AutoHotCorner on others
- Supports two monitors, 4 corners each, each corner triggers up to 3-key hotkey combo
- Corner detection by exact position match to calibrated coordinates (kept for precision),
  with optional tolerance setting (pixels) to broaden detection if desired.
"""

import os
import sys
import json
import pyautogui
import platform
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu, QLineEdit, QFileDialog, QStyle
)


APP_NAME = "AutoHotCorner"
VERSION = "2.0"

# ----------------------------- Utilities -----------------------------

def app_config_dir() -> Path:
    if platform.system() == "Windows":
        base = os.getenv("APPDATA") or str(Path.home() / "AppData/Roaming")
        return Path(base) / APP_NAME
    else:
        return Path.home() / ".config" / APP_NAME

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def config_path() -> Path:
    ensure_dir(app_config_dir())
    return app_config_dir() / "config.json"

def load_config() -> dict:
    p = config_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    # defaults
    return {
        "selected_key": "f15",       # key for periodic keep-alive press
        "cycle_min": 1,              # minutes
        "use_monitor": [False, False],
        # hotkeys: 4 corners x 3 keys each (strings: 'none' or pyautogui key names)
        "hotkeys": [
            ["none", "none", "none"],  # LT
            ["none", "none", "none"],  # RT
            ["none", "none", "none"],  # LB
            ["none", "none", "none"],  # RB
        ],
        # calibration: [ [x,y] * 4 corners ] * 2 monitors, all strings for easy display
        "calibration": [
            [["0","0"],["0","0"],["0","0"],["0","0"]],  # monitor 1: LT,RT,LB,RB
            [["0","0"],["0","0"],["0","0"],["0","0"]],  # monitor 2
        ],
        "tolerance_px": 0
    }

def save_config(cfg: dict):
    try:
        config_path().write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to save config:", e)

# Map Qt key names to pyautogui names when possible
SPECIAL_MAP = {
    "escape":"esc","ctrl":"ctrl","control":"ctrl","alt":"alt","shift":"shift","win":"win",
    "left":"left","right":"right","up":"up","down":"down",
    "tab":"tab","capslock":"capslock",
    "f1":"f1","f2":"f2","f3":"f3","f4":"f4","f5":"f5","f6":"f6","f7":"f7","f8":"f8","f9":"f9","f10":"f10","f11":"f11","f12":"f12",
}

def normalize_key(txt: str) -> str:
    """
    Normalize user text to pyautogui key string; fall back to lowercase ascii letters/digits.
    """
    if not txt:
        return "none"
    s = txt.strip().lower()
    if s in SPECIAL_MAP:
        return SPECIAL_MAP[s]
    if len(s) == 1:  # single character like 'a', 'b', '1'
        return s
    return s  # pyautogui accepts many names as-is (e.g., 'enter', 'home', etc.)

def pyauto_press_combo(keys):
    # keys is a list like ['ctrl','alt','k'] (already normalized, and 'none' filtered out)
    if not keys:
        return
    for k in keys[:-1]:
        pyautogui.keyDown(k)
    pyautogui.press(keys[-1])
    for k in reversed(keys[:-1]):
        pyautogui.keyUp(k)

# ----------------------------- Key Capture Mini-Dialog -----------------------------

class KeyCapture(QWidget):
    """
    Lightweight key-capture window:
    - When opened, the user presses a key (or combination with modifiers).
    - We parse modifiers + last key into up to 3 pyautogui keys.
    - ESC to set 'none'.
    """
    def __init__(self, on_done):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(280, 120)
        self.setWindowTitle("키 입력")
        self.on_done = on_done
        self.label = QLabel("입력: (Ctrl/Alt/Shift + Key 가능)\nESC = None", self)
        self.label.setAlignment(Qt.AlignCenter)
        lay = QVBoxLayout(self)
        lay.addWidget(self.label)

    def keyPressEvent(self, e):
        key = e.key()
        mods = e.modifiers()

        if key == Qt.Key_Escape:
            self.on_done(["none"])
            self.close()
            return

        parts = []
        if mods & Qt.ControlModifier: parts.append("ctrl")
        if mods & Qt.AltModifier: parts.append("alt")
        if mods & Qt.ShiftModifier: parts.append("shift")
        if mods & Qt.MetaModifier: parts.append("win")

        # Last key name
        qt_to_name = {
            Qt.Key_Left:"left", Qt.Key_Right:"right", Qt.Key_Up:"up", Qt.Key_Down:"down",
            Qt.Key_Tab:"tab", Qt.Key_CapsLock:"capslock",
            Qt.Key_F1:"f1",Qt.Key_F2:"f2",Qt.Key_F3:"f3",Qt.Key_F4:"f4",Qt.Key_F5:"f5",Qt.Key_F6:"f6",
            Qt.Key_F7:"f7",Qt.Key_F8:"f8",Qt.Key_F9:"f9",Qt.Key_F10:"f10",Qt.Key_F11:"f11",Qt.Key_F12:"f12",
            Qt.Key_Return:"enter", Qt.Key_Enter:"enter", Qt.Key_Backspace:"backspace", Qt.Key_Delete:"delete",
            Qt.Key_Home:"home", Qt.Key_End:"end", Qt.Key_PageUp:"pageup", Qt.Key_PageDown:"pagedown",
            Qt.Key_Space:"space",
        }
        if key in qt_to_name:
            parts.append(qt_to_name[key])
        else:
            ch = e.text()
            if ch:
                parts.append(ch.lower())

        parts = [normalize_key(p) for p in parts if p]

        # Restrict to max 3 keys (mod1, mod2, key)
        parts = parts[:3] if parts else ["none"]
        self.on_done(parts)
        self.close()

# ----------------------------- Main Window -----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Core state
        self.cfg = load_config()
        self.status_running = False

        # PyAutoGUI failsafe off (so you can move mouse to corners without aborting)
        pyautogui.FAILSAFE = False

        # Timers
        self.keepalive_timer = QTimer(self)  # presses a key every N minutes
        self.keepalive_timer.timeout.connect(self._do_keepalive)

        self.corner_timer = QTimer(self)     # checks mouse position at ~60Hz
        self.corner_timer.timeout.connect(self._poll_mouse)
        self.corner_timer.start(16)

        # Build UI
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(QSize(420, 640))
        self.setWindowIcon(QIcon.fromTheme("input-keyboard"))

        root = QWidget(self)
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(14,14,14,14)
        outer.setSpacing(12)

        # --- Status + Start/Stop ---
        header = QHBoxLayout()
        self.label_status = QLabel("상태 : Stop")
        self.btn_toggle = QPushButton("Start")
        self.btn_toggle.clicked.connect(self.toggle_start_stop)
        header.addWidget(self.label_status)
        header.addStretch(1)
        header.addWidget(self.btn_toggle)
        outer.addLayout(header)

        # --- Keepalive group ---
        keep_grp = QGroupBox("주기적 키 입력 (선택 사항)")
        keep_lay = QHBoxLayout(keep_grp)
        keep_lay.addWidget(QLabel("키:"))
        self.combo_key = QComboBox()
        # A compact set of reasonable keys; advanced users can type manually too
        for k in ["f15","scrolllock","shift","ctrl","alt","win","tab","enter","esc","space"]:
            self.combo_key.addItem(k)
        # allow custom text
        self.combo_key.setEditable(True)
        self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))
        keep_lay.addWidget(self.combo_key)

        keep_lay.addWidget(QLabel("주기(분):"))
        self.spin_cycle = QSpinBox()
        self.spin_cycle.setRange(1, 720)
        self.spin_cycle.setValue(int(self.cfg.get("cycle_min", 1)))
        keep_lay.addWidget(self.spin_cycle)
        outer.addWidget(keep_grp)

        # --- Hotkeys group ---
        hk_grp = QGroupBox("핫코너 ↦ 단축키")
        hk_lay = QGridLayout(hk_grp)
        outer.addWidget(hk_grp)

        # 4 corners rows
        self.hotkey_btns = []  # 4 corners x 3 buttons
        corner_names = ["좌상(LT)","우상(RT)","좌하(LB)","우하(RB)"]
        for row in range(4):
            hk_lay.addWidget(QLabel(corner_names[row]), row, 0)
            row_btns = []
            for col in range(3):
                b = QPushButton(self.cfg["hotkeys"][row][col].upper())
                b.setObjectName(f"hk_{row}_{col}")
                b.clicked.connect(self._on_hotkey_assign)
                hk_lay.addWidget(b, row, col+1)
                row_btns.append(b)
            self.hotkey_btns.append(row_btns)

        # --- Calibration group ---
        cal_grp = QGroupBox("좌표 보정 (코너 지정)")
        cal_lay = QGridLayout(cal_grp)
        outer.addWidget(cal_grp)

        # Monitor toggles
        self.chk_mon1 = QCheckBox("모니터 1 사용")
        self.chk_mon2 = QCheckBox("모니터 2 사용")
        self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
        self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))
        cal_lay.addWidget(self.chk_mon1, 0, 0, 1, 2)
        cal_lay.addWidget(self.chk_mon2, 0, 2, 1, 2)

        # Tolerance
        cal_lay.addWidget(QLabel("허용 오차(px):"), 1, 0)
        self.tol_edit = QLineEdit(str(self.cfg.get("tolerance_px", 0)))
        self.tol_edit.setFixedWidth(60)
        cal_lay.addWidget(self.tol_edit, 1, 1)

        # Calibration buttons grid
        self.cal_btns = []  # [ [LT,RT,LB,RB], [LT,RT,LB,RB] ]
        for mon in range(2):
            for cidx, cname in enumerate(["LT","RT","LB","RB"]):
                idx_row = 2 + mon
                col = cidx
                text = ".".join(self.cfg["calibration"][mon][cidx])
                b = QPushButton(f"M{mon+1}-{cname}: {text}")
                b.setObjectName(f"cal_{mon}_{cidx}")
                b.setToolTip("포인터를 원하는 좌표에 두고 Enter (ESC 취소)")
                b.clicked.connect(self._start_calibration)
                cal_lay.addWidget(b, idx_row, col)

        # --- Actions ---
        actions = QHBoxLayout()
        self.btn_save = QPushButton("저장")
        self.btn_save.clicked.connect(self._save_clicked)
        self.btn_quit = QPushButton("종료")
        self.btn_quit.clicked.connect(self.close)
        actions.addStretch(1)
        actions.addWidget(self.btn_save)
        actions.addWidget(self.btn_quit)
        outer.addLayout(actions)

        # System tray
        self.tray = QSystemTrayIcon(self)
        # Use a generic icon if theme icon missing
        icon = QIcon.fromTheme("input-keyboard")
        if icon.isNull():
            self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        else:
            self.tray.setIcon(icon)
        self.tray.setToolTip("상태 : Stop")
        m = QMenu()
        act_show = m.addAction("Show")
        act_hide = m.addAction("Hide")
        m.addSeparator()
        act_toggle = m.addAction("Start/Stop")
        m.addSeparator()
        act_exit = m.addAction("Exit")
        act_show.triggered.connect(self.showNormal)
        act_hide.triggered.connect(self.hide)
        act_toggle.triggered.connect(self.toggle_start_stop)
        act_exit.triggered.connect(self.close)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

        # Styling
        self._apply_style()

        # Internal state for corner-detection cooldown
        self._cooldown = False
        self._cooldown_timer = QTimer(self)
        self._cooldown_timer.setSingleShot(True)
        self._cooldown_timer.timeout.connect(lambda: setattr(self, "_cooldown", False))

    # ----------------------------- Styling -----------------------------
    def _apply_style(self):
        self.setStyleSheet("""
            QWidget { font-size: 13px; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 10px;
                margin-top: 10px;
                padding: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QPushButton {
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #666;
            }
            QPushButton:hover { background: #2a2a2a; }
            QPushButton:pressed { background: #1f1f1f; }
            QLineEdit, QSpinBox, QComboBox {
                padding: 6px 8px;
                border-radius: 6px;
                border: 1px solid #666;
            }
        """)

    # ----------------------------- System Tray -----------------------------
    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    # ----------------------------- Hotkey Assign -----------------------------
    def _on_hotkey_assign(self):
        sender = self.sender()
        ident = sender.objectName()     # hk_r_c
        _, r, c = ident.split("_")
        r, c = int(r), int(c)

        def done(keys_list):
            # we only store up to 3 keys; pad with 'none'
            keys = [k for k in keys_list if k != "none"]
            while len(keys) < 3:
                keys.append("none")
            keys = keys[:3]
            self.cfg["hotkeys"][r] = keys
            sender.setText(keys[c].upper())  # update only the clicked cell text
            # also update other cells in the row for visual consistency
            for j, btn in enumerate(self.hotkey_btns[r]):
                btn.setText(self.cfg["hotkeys"][r][j].upper())

        cap = KeyCapture(done)
        cap.move(self.geometry().center() - cap.rect().center())
        cap.show()

    # ----------------------------- Calibration -----------------------------
    def _start_calibration(self):
        sender = self.sender()
        _, mon, corner = sender.objectName().split("_")
        mon, corner = int(mon), int(corner)

        # Show small banner and wait for Enter
        msg = QMessageBox(self)
        msg.setWindowTitle("좌표 보정")
        msg.setText("원하는 지점에 마우스를 놓고 Enter 를 누르세요. (ESC 취소)")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.button(QMessageBox.Ok).setText("대기")
        msg.button(QMessageBox.Cancel).setText("취소")
        # We simulate "waiting" by grabbing the next key-press on the app
        msg.show()

        # Temporarily install an event filter to catch Enter/Esc globally
        self._calib_waiting = True

        def key_filter(obj, ev):
            from PyQt5.QtCore import QEvent
            if ev.type() == QEvent.KeyPress and self._calib_waiting:
                if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                    x = str(pyautogui.position().x)
                    y = str(pyautogui.position().y)
                    self.cfg["calibration"][mon][corner] = [x, y]
                    sender.setText(f"M{mon+1}-{'LTRT LBRB'.split()[corner] if False else ['LT','RT','LB','RB'][corner]}: {x}.{y}")
                    self._calib_waiting = False
                    msg.accept()
                    self.removeEventFilter(self._event_filter)
                    return True
                elif ev.key() == Qt.Key_Escape:
                    self._calib_waiting = False
                    msg.reject()
                    self.removeEventFilter(self._event_filter)
                    return True
            return False

        self._event_filter = type("EF",(object,),{"eventFilter":key_filter})()
        self.installEventFilter(self._event_filter)

    # ----------------------------- Start/Stop -----------------------------
    def toggle_start_stop(self):
        if not self.status_running:
            # start
            key = normalize_key(self.combo_key.currentText())
            if key == "none":
                # Allow none (no keepalive), but we'll still run corner detection.
                pass
            self.cfg["selected_key"] = key
            self.cfg["cycle_min"] = int(self.spin_cycle.value())

            ms = max(1, int(self.spin_cycle.value())) * 60_000
            self.keepalive_timer.stop()
            if key != "none":
                self.keepalive_timer.start(ms)

            self.status_running = True
            self.label_status.setText("상태 : Run")
            self.tray.setToolTip("상태 : Run")
            self.btn_toggle.setText("Stop")
        else:
            # stop
            self.keepalive_timer.stop()
            self.status_running = False
            self.label_status.setText("상태 : Stop")
            self.tray.setToolTip("상태 : Stop")
            self.btn_toggle.setText("Start")

    def _do_keepalive(self):
        key = self.cfg.get("selected_key","f15")
        try:
            pyautogui.press(key)
            pyautogui.press(key)
        except Exception as e:
            print("Keepalive press failed:", e)

    # ----------------------------- Corner Polling -----------------------------
    def _poll_mouse(self):
        # cooldown prevents repetitive triggers while cursor sits on the corner
        if self._cooldown or not self.status_running:
            return

        use1, use2 = self.chk_mon1.isChecked(), self.chk_mon2.isChecked()
        tol = 0
        try:
            tol = max(0, int(self.tol_edit.text()))
        except Exception:
            pass

        pos = pyautogui.position()
        curx, cury = str(pos.x), str(pos.y)

        # Build match list: [(row index, [ (mon,x,y) pairs ])]
        checks = [
            (0, []), (1, []), (2, []), (3, [])
        ]
        # Append monitor entries based on enabled flags
        if use1:
            for idx in range(4):
                checks[idx][1].append( (0, *self.cfg["calibration"][0][idx]) )
        if use2:
            for idx in range(4):
                checks[idx][1].append( (1, *self.cfg["calibration"][1][idx]) )

        # Helper: exact or tolerance match
        def match(ax, ay):
            if tol <= 0:
                return (curx == ax and cury == ay)
            try:
                return (abs(int(curx)-int(ax)) <= tol) and (abs(int(cury)-int(ay)) <= tol)
            except Exception:
                return False

        # iterate corners
        for corner_idx, entries in checks:
            for mon, ax, ay in entries:
                if match(ax, ay):
                    self._trigger_corner(corner_idx)
                    self._cooldown = True
                    self._cooldown_timer.start(500)  # 0.5s cooldown
                    return

    def _trigger_corner(self, corner_idx: int):
        # Get keys for the corner, filter 'none'
        keys = [normalize_key(k) for k in self.cfg["hotkeys"][corner_idx] if normalize_key(k) != "none"]
        try:
            pyauto_press_combo(keys)
        except Exception as e:
            print("Corner hotkey failed:", e)

    # ----------------------------- Save -----------------------------
    def _save_clicked(self):
        # persist toggles & tolerance
        self.cfg["use_monitor"][0] = self.chk_mon1.isChecked()
        self.cfg["use_monitor"][1] = self.chk_mon2.isChecked()
        try:
            self.cfg["tolerance_px"] = max(0, int(self.tol_edit.text()))
        except Exception:
            self.cfg["tolerance_px"] = 0

        # also persist keepalive fields
        self.cfg["selected_key"] = normalize_key(self.combo_key.currentText())
        self.cfg["cycle_min"] = int(self.spin_cycle.value())

        save_config(self.cfg)
        QMessageBox.information(self, "저장됨", "설정이 저장되었습니다.")

    # ----------------------------- Window Events -----------------------------
    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()

    def closeEvent(self, event):
        # Stop timers and hide tray
        self.keepalive_timer.stop()
        self.corner_timer.stop()
        self.tray.hide()
        save_config(self.cfg)
        event.accept()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
