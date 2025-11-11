# -*- coding: utf-8 -*-
"""
AutoHotCorner v3 (PyQt5, single-file)
- Fully coded UI (no .ui)
- Modern dark theme + tabbed layout
- System tray menu with Start/Stop & Show/Hide
- Non-blocking timers; friendly messages & tooltips
- Per-corner up to 3-key combinations (e.g., Ctrl+Alt+K)
- Two-monitor support, tolerance pixels, cooldown to avoid retriggers
- Config export/import/reset; persistent settings
- FIXES:
  1) CapsLock / NumLock keys added
  2) Key capture uses modal QDialog.exec_() so it won't flash/auto-close
  3) Calibration uses a modal dialog (no fragile event filters)
  4) Windows config path bug fixed
"""

import os, sys, json, platform
import pyautogui
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu, QLineEdit, QFileDialog, QTabWidget, QStyle, QDialog
)

APP_NAME = "AutoHotCorner"
VERSION = "3.0"

# ----------------------------- Utilities -----------------------------

def default_config() -> dict:
    return {
        "selected_key": "f15",
        "cycle_min": 1,
        "use_monitor": [False, False],
        "hotkeys": [
            ["none","none","none"],  # LT
            ["none","none","none"],  # RT
            ["none","none","none"],  # LB
            ["none","none","none"],  # RB
        ],
        "calibration": [
            [["0","0"],["0","0"],["0","0"],["0","0"]],
            [["0","0"],["0","0"],["0","0"],["0","0"]],
        ],
        "tolerance_px": 0
    }

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
            data = json.loads(p.read_text(encoding="utf-8"))
            # shallow sanity
            if not isinstance(data, dict): raise ValueError("bad cfg")
            return data
        except Exception:
            pass
    return default_config()

def save_config(cfg: dict):
    try:
        config_path().write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to save config:", e)

# Add CapsLock / NumLock mapping
SPECIAL_MAP = {
    "escape":"esc","esc":"esc","ctrl":"ctrl","control":"ctrl","alt":"alt","shift":"shift","win":"win",
    "left":"left","right":"right","up":"up","down":"down",
    "tab":"tab","capslock":"capslock","numlock":"numlock",
    "f1":"f1","f2":"f2","f3":"f3","f4":"f4","f5":"f5","f6":"f6","f7":"f7","f8":"f8","f9":"f9","f10":"f10","f11":"f11","f12":"f12",
    "enter":"enter","space":"space","backspace":"backspace","delete":"delete","home":"home","end":"end",
    "pageup":"pageup","pagedown":"pagedown"
}

def normalize_key(txt: str) -> str:
    if not txt:
        return "none"
    s = txt.strip().lower()
    if s in SPECIAL_MAP:
        return SPECIAL_MAP[s]
    if len(s) == 1:
        return s
    return s

def pyauto_press_combo(keys):
    if not keys:
        return
    for k in keys[:-1]:
        pyautogui.keyDown(k)
    pyautogui.press(keys[-1])
    for k in reversed(keys[:-1]):
        pyautogui.keyUp(k)

# ----------------------------- Modal dialogs -----------------------------

class KeyCaptureDialog(QDialog):
    """
    Modal dialog that captures a single key press (optionally with modifiers).
    Returns up to 3 keys. ESC returns ["none"].
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("키 입력")
        self.setModal(True)
        self.setFixedSize(320, 140)
        lbl = QLabel("입력 대기중...\n(Ctrl/Alt/Shift/Win + Key 가능, ESC=없음)")
        lbl.setAlignment(Qt.AlignCenter)
        lay = QVBoxLayout(self)
        lay.addWidget(lbl)
        # Ensure keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

    @staticmethod
    def capture(parent=None):
        dlg = KeyCaptureDialog(parent)
        # Show and focus
        dlg.show()
        dlg.activateWindow()
        dlg.raise_()
        dlg.setFocus()
        result = dlg.exec_()  # modal loop
        return getattr(dlg, "_result", ["none"])

    def keyPressEvent(self, e):
        key = e.key()
        mods = e.modifiers()
        if key == Qt.Key_Escape:
            self._result = ["none"]
            self.accept()
            return

        parts = []
        if mods & Qt.ControlModifier: parts.append("ctrl")
        if mods & Qt.AltModifier: parts.append("alt")
        if mods & Qt.ShiftModifier: parts.append("shift")
        if mods & Qt.MetaModifier: parts.append("win")

        qt_map = {
            Qt.Key_Left:"left", Qt.Key_Right:"right", Qt.Key_Up:"up", Qt.Key_Down:"down",
            Qt.Key_Tab:"tab", Qt.Key_CapsLock:"capslock", Qt.Key_NumLock:"numlock",
            Qt.Key_F1:"f1",Qt.Key_F2:"f2",Qt.Key_F3:"f3",Qt.Key_F4:"f4",Qt.Key_F5:"f5",Qt.Key_F6:"f6",
            Qt.Key_F7:"f7",Qt.Key_F8:"f8",Qt.Key_F9:"f9",Qt.Key_F10:"f10",Qt.Key_F11:"f11",Qt.Key_F12:"f12",
            Qt.Key_Return:"enter", Qt.Key_Enter:"enter", Qt.Key_Backspace:"backspace", Qt.Key_Delete:"delete",
            Qt.Key_Home:"home", Qt.Key_End:"end", Qt.Key_PageUp:"pageup", Qt.Key_PageDown:"pagedown",
            Qt.Key_Space:"space",
        }
        if key in qt_map:
            parts.append(qt_map[key])
        else:
            ch = e.text()
            if ch:
                parts.append(ch.lower())

        parts = [normalize_key(p) for p in parts if p]
        if not parts:
            parts = ["none"]
        self._result = parts[:3]
        self.accept()

class CalibrationDialog(QDialog):
    """
    Modal dialog that waits for Enter to capture current mouse position (pyautogui.position()).
    ESC cancels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("좌표 보정")
        self.setModal(True)
        self.setFixedSize(360, 160)
        lay = QVBoxLayout(self)
        self.lbl = QLabel("원하는 위치에 마우스를 두고 Enter.\n취소는 ESC")
        self.lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.lbl)
        self.setFocusPolicy(Qt.StrongFocus)

    @staticmethod
    def capture(parent=None):
        dlg = CalibrationDialog(parent)
        dlg.show()
        dlg.activateWindow()
        dlg.raise_()
        dlg.setFocus()
        ok = dlg.exec_()
        return getattr(dlg, "_pos", None)  # (x,y) or None

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            p = pyautogui.position()
            self._pos = (str(p.x), str(p.y))
            self.accept()
        elif e.key() == Qt.Key_Escape:
            self._pos = None
            self.reject()

# ----------------------------- Theme -----------------------------

def apply_dark_theme(app: QApplication):
    pal = QPalette()
    base = QColor(30,30,33)
    alt = QColor(40,40,45)
    text = QColor(230,230,235)
    acc = QColor(90,130,255)

    pal.setColor(QPalette.Window, base)
    pal.setColor(QPalette.WindowText, text)
    pal.setColor(QPalette.Base, alt)
    pal.setColor(QPalette.AlternateBase, base)
    pal.setColor(QPalette.ToolTipBase, alt)
    pal.setColor(QPalette.ToolTipText, text)
    pal.setColor(QPalette.Text, text)
    pal.setColor(QPalette.Button, alt)
    pal.setColor(QPalette.ButtonText, text)
    pal.setColor(QPalette.Highlight, acc)
    pal.setColor(QPalette.HighlightedText, QColor(255,255,255))
    app.setPalette(pal)

CARD_QSS = """
QGroupBox {
    font-weight: 600;
    border: 1px solid #3c3c44;
    border-radius: 12px;
    margin-top: 14px;
    padding: 10px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; }
QPushButton {
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #555;
}
QPushButton:hover { background: #2f2f36; }
QPushButton:pressed { background: #27272e; }
QLineEdit, QSpinBox, QComboBox {
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid #555;
}
QTabWidget::pane { border: 1px solid #3c3c44; border-radius: 10px; }
QTabBar::tab {
    padding: 8px 14px; margin: 4px;
    border: 1px solid #444; border-radius: 8px;
}
QTabBar::tab:selected { background: #2a2a31; }
"""

def status_pill(text: str, ok: bool) -> str:
    color = "#1fbf75" if ok else "#d9534f"
    return f"<span style='background:{color};color:#fff;padding:3px 8px;border-radius:10px;'>{text}</span>"

# ----------------------------- Main Window -----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cfg = load_config()
        self.status_running = False
        self._cooldown = False

        pyautogui.FAILSAFE = False

        self.keepalive_timer = QTimer(self)
        self.keepalive_timer.timeout.connect(self._do_keepalive)

        self.corner_timer = QTimer(self)
        self.corner_timer.timeout.connect(self._poll_mouse)
        self.corner_timer.start(16)

        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)
        self.cooldown_timer.timeout.connect(lambda: setattr(self, "_cooldown", False))

        # Window
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(560, 720)

        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setElideMode(Qt.ElideRight)
        self.setCentralWidget(tabs)

        # Dashboard
        self.page_dash = QWidget()
        v = QVBoxLayout(self.page_dash); v.setSpacing(10)
        # Controls
        ctrl = QGroupBox("컨트롤"); lay = QHBoxLayout(ctrl)
        self.btn_toggle = QPushButton("Start")
        self.btn_toggle.setToolTip("핫코너 감지를 시작/중지합니다.")
        self.btn_toggle.clicked.connect(self.toggle_start_stop)

        self.combo_key = QComboBox(); self.combo_key.setEditable(True)
        for k in ["f15","scrolllock","shift","ctrl","alt","win","tab","enter","esc","space","capslock","numlock","none"]:
            self.combo_key.addItem(k)
        self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))

        self.spin_cycle = QSpinBox(); self.spin_cycle.setRange(1, 720)
        self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))

        form = QGridLayout()
        form.addWidget(QLabel("주기 키:"),0,0); form.addWidget(self.combo_key,0,1)
        form.addWidget(QLabel("주기(분):"),1,0); form.addWidget(self.spin_cycle,1,1)

        self.lbl_status = QLabel(status_pill("Stop", False))

        lay.addLayout(form); lay.addStretch(1); lay.addWidget(self.lbl_status); lay.addWidget(self.btn_toggle)
        v.addWidget(ctrl)

        # Live info
        card2 = QGroupBox("실시간 정보")
        ly2 = QGridLayout(card2)
        self.lbl_mouse = QLabel("마우스: -, -")
        self.lbl_tip = QLabel("코너에 마우스를 두면 등록된 단축키가 실행됩니다.")
        self.lbl_tip.setStyleSheet("color:#aaaaae;")
        ly2.addWidget(self.lbl_mouse,0,0)
        ly2.addWidget(self.lbl_tip,1,0)
        v.addWidget(card2)

        # Quick test
        card3 = QGroupBox("빠른 테스트")
        ly3 = QHBoxLayout(card3)
        for i, name in enumerate(["LT","RT","LB","RB"]):
            b = QPushButton(f"{name} 실행")
            b.clicked.connect(lambda _, idx=i: self._trigger_corner(idx))
            ly3.addWidget(b)
        v.addWidget(card3)
        v.addStretch(1)

        # Hotkeys page
        self.page_hot = QWidget()
        v2 = QVBoxLayout(self.page_hot); v2.setSpacing(10)
        gb = QGroupBox("핫코너 ↦ 단축키 지정"); gl = QGridLayout(gb)
        self.hotkey_btns = []
        names = ["좌상(LT)","우상(RT)","좌하(LB)","우하(RB)"]
        for r in range(4):
            gl.addWidget(QLabel(names[r]), r, 0)
            row_btns = []
            for c in range(3):
                txt = self.cfg["hotkeys"][r][c].upper()
                b = QPushButton(txt)
                b.setObjectName(f"hk_{r}_{c}")
                b.setToolTip("클릭 후 원하는 키 조합을 입력하세요 (ESC=없음)")
                b.clicked.connect(self._on_hotkey_assign)
                gl.addWidget(b, r, c+1)
                row_btns.append(b)
            self.hotkey_btns.append(row_btns)
        hint = QLabel("팁: Ctrl/Alt/Shift/Win + Key 조합을 지원합니다. 최대 3키.")
        hint.setStyleSheet("color:#aaaaae;")
        v2.addWidget(gb); v2.addWidget(hint); v2.addStretch(1)

        # Calibration page
        self.page_cal = QWidget()
        v3 = QVBoxLayout(self.page_cal); v3.setSpacing(10)
        gb2 = QGroupBox("코너 좌표 보정 & 사용 모니터"); gl2 = QGridLayout(gb2)

        self.chk_mon1 = QCheckBox("모니터 1 사용"); self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
        self.chk_mon2 = QCheckBox("모니터 2 사용"); self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))

        gl2.addWidget(self.chk_mon1, 0, 0)
        gl2.addWidget(self.chk_mon2, 0, 1)

        gl2.addWidget(QLabel("허용 오차(px):"), 1, 0)
        self.tol_edit = QLineEdit(str(self.cfg.get("tolerance_px",0))); self.tol_edit.setFixedWidth(80)
        gl2.addWidget(self.tol_edit, 1, 1)

        # Calibration buttons
        self.cal_btns = []
        for mon in range(2):
            for idx, cname in enumerate(["LT","RT","LB","RB"]):
                x, y = self.cfg["calibration"][mon][idx]
                b = QPushButton(f"M{mon+1}-{cname}: {x}.{y}")
                b.setObjectName(f"cal_{mon}_{idx}")
                b.setToolTip("포인터를 원하는 위치로 옮긴 뒤 Enter (ESC 취소)")
                b.clicked.connect(self._start_calibration)
                gl2.addWidget(b, 2+mon, idx)
        v3.addWidget(gb2)
        tip = QLabel("보정하지 않으면 (0,0) 등 기본 좌표로 인식됩니다.")
        tip.setStyleSheet("color:#aaaaae;")
        v3.addWidget(tip); v3.addStretch(1)

        # Settings page
        self.page_set = QWidget()
        v4 = QVBoxLayout(self.page_set); v4.setSpacing(10)
        gb3 = QGroupBox("설정"); gl3 = QGridLayout(gb3)
        self.btn_save = QPushButton("저장"); self.btn_save.clicked.connect(self._save_clicked)
        self.btn_export = QPushButton("내보내기"); self.btn_export.clicked.connect(self._export_cfg)
        self.btn_import = QPushButton("가져오기"); self.btn_import.clicked.connect(self._import_cfg)
        self.btn_reset = QPushButton("초기화"); self.btn_reset.clicked.connect(self._reset_cfg)
        gl3.addWidget(QLabel(f"설정 경로: {config_path()}"), 0, 0, 1, 4)
        gl3.addWidget(self.btn_save, 1, 0)
        gl3.addWidget(self.btn_export, 1, 1)
        gl3.addWidget(self.btn_import, 1, 2)
        gl3.addWidget(self.btn_reset, 1, 3)
        v4.addWidget(gb3)
        about = QGroupBox("About")
        ab_l = QVBoxLayout(about)
        ab_l.addWidget(QLabel(f"{APP_NAME} v{VERSION} — 윈도우에서 핫코너를 편리하게."))
        v4.addWidget(about); v4.addStretch(1)

        # Add tabs
        tabs.addTab(self.page_dash, "Dashboard")
        tabs.addTab(self.page_hot, "Hotcorners")
        tabs.addTab(self.page_cal, "Calibration")
        tabs.addTab(self.page_set, "Settings")

        # Tray
        self.tray = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.setToolTip("AutoHotCorner")
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

        self.setStyleSheet(CARD_QSS)

    # --- Tray ---
    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    # --- Actions ---
    def toggle_start_stop(self):
        start = not self.status_running
        key = normalize_key(self.combo_key.currentText())

        self.cfg["selected_key"] = key
        self.cfg["cycle_min"] = int(self.spin_cycle.value())

        if start:
            ms = max(1, int(self.spin_cycle.value())) * 60_000
            self.keepalive_timer.stop()
            if key != "none":
                self.keepalive_timer.start(ms)
            self.status_running = True
            self.lbl_status.setText(status_pill("Run", True))
            self.btn_toggle.setText("Stop")
        else:
            self.keepalive_timer.stop()
            self.status_running = False
            self.lbl_status.setText(status_pill("Stop", False))
            self.btn_toggle.setText("Start")

    def _do_keepalive(self):
        key = self.cfg.get("selected_key","f15")
        try:
            pyautogui.press(key); pyautogui.press(key)
        except Exception as e:
            print("Keepalive press failed:", e)

    def _poll_mouse(self):
        # live mouse label always updates
        pos = pyautogui.position()
        self.lbl_mouse.setText(f"마우스: {pos.x}, {pos.y}")

        if self._cooldown or not self.status_running:
            return

        use1, use2 = self.chk_mon1.isChecked(), self.chk_mon2.isChecked()
        try:
            tol = max(0, int(self.tol_edit.text()))
        except Exception:
            tol = 0

        curx, cury = pos.x, pos.y

        checks = {0:[], 1:[], 2:[], 3:[]}
        if use1:
            for idx in range(4):
                ax, ay = self.cfg["calibration"][0][idx]
                checks[idx].append((0, int(ax), int(ay)))
        if use2:
            for idx in range(4):
                ax, ay = self.cfg["calibration"][1][idx]
                checks[idx].append((1, int(ax), int(ay)))

        def match(ax, ay):
            if tol <= 0:
                return (curx == ax and cury == ay)
            return abs(curx-ax) <= tol and abs(cury-ay) <= tol

        for corner_idx, entries in checks.items():
            for mon, ax, ay in entries:
                if match(ax, ay):
                    self._trigger_corner(corner_idx)
                    self._cooldown = True
                    self.cooldown_timer.start(500)
                    return

    def _trigger_corner(self, idx: int):
        keys = [normalize_key(k) for k in self.cfg["hotkeys"][idx] if normalize_key(k) != "none"]
        try:
            pyauto_press_combo(keys)
        except Exception as e:
            print("Corner hotkey failed:", e)

    def _on_hotkey_assign(self):
        sender = self.sender()
        _, r, c = sender.objectName().split("_")
        r, c = int(r), int(c)

        keys_list = KeyCaptureDialog.capture(self)
        # standardize to length 3
        keys = [k for k in keys_list if k != "none"]
        while len(keys) < 3:
            keys.append("none")
        keys = keys[:3]
        self.cfg["hotkeys"][r] = keys
        # update row buttons
        for j, btn in enumerate(self.hotkey_btns[r]):
            btn.setText(self.cfg["hotkeys"][r][j].upper())

    def _start_calibration(self):
        sender = self.sender()
        _, mon, corner = sender.objectName().split("_")
        mon, corner = int(mon), int(corner)

        pos = CalibrationDialog.capture(self)
        if pos is None:
            return
        x, y = pos
        self.cfg["calibration"][mon][corner] = [x, y]
        cname = ["LT","RT","LB","RB"][corner]
        sender.setText(f"M{mon+1}-{cname}: {x}.{y}")

    # --- Settings helpers ---
    def _save_clicked(self):
        self.cfg["use_monitor"][0] = self.chk_mon1.isChecked()
        self.cfg["use_monitor"][1] = self.chk_mon2.isChecked()
        try:
            self.cfg["tolerance_px"] = max(0, int(self.tol_edit.text()))
        except Exception:
            self.cfg["tolerance_px"] = 0
        self.cfg["selected_key"] = normalize_key(self.combo_key.currentText())
        self.cfg["cycle_min"] = int(self.spin_cycle.value())

        save_config(self.cfg)
        QMessageBox.information(self, "저장됨", "설정이 저장되었습니다.")

    def _export_cfg(self):
        path, _ = QFileDialog.getSaveFileName(self, "설정 내보내기", str(Path.home() / "AutoHotCorner.json"), "JSON (*.json)")
        if not path: return
        try:
            Path(path).write_text(json.dumps(self.cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            QMessageBox.information(self, "완료", "설정을 내보냈습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"내보내기 실패: {e}")

    def _import_cfg(self):
        path, _ = QFileDialog.getOpenFileName(self, "설정 가져오기", str(Path.home()), "JSON (*.json)")
        if not path: return
        try:
            cfg = json.loads(Path(path).read_text(encoding="utf-8"))
            self.cfg = cfg
            # refresh UI bits
            self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))
            self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))
            self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
            self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))
            self.tol_edit.setText(str(self.cfg.get("tolerance_px",0)))
            for r in range(4):
                for c in range(3):
                    self.hotkey_btns[r][c].setText(self.cfg["hotkeys"][r][c].upper())
            for mon in range(2):
                for idx in range(4):
                    x,y = self.cfg["calibration"][mon][idx]
                    btn = self.findChild(QPushButton, f"cal_{mon}_{idx}")
                    if btn:
                        cname = ["LT","RT","LB","RB"][idx]
                        btn.setText(f"M{mon+1}-{cname}: {x}.{y}")
            QMessageBox.information(self, "완료", "설정을 가져왔습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"가져오기 실패: {e}")

    def _reset_cfg(self):
        self.cfg = default_config()
        save_config(self.cfg)
        # refresh UI
        self.combo_key.setCurrentText(self.cfg["selected_key"])
        self.spin_cycle.setValue(self.cfg["cycle_min"])
        self.chk_mon1.setChecked(False); self.chk_mon2.setChecked(False)
        self.tol_edit.setText("0")
        for r in range(4):
            for c in range(3):
                self.hotkey_btns[r][c].setText("NONE")
        for mon in range(2):
            for idx in range(4):
                btn = self.findChild(QPushButton, f"cal_{mon}_{idx}")
                if btn:
                    cname = ["LT","RT","LB","RB"][idx]
                    btn.setText(f"M{mon+1}-{cname}: 0.0")
        QMessageBox.information(self, "초기화", "설정을 초기화했습니다.")

    # --- Window Events ---
    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()

    def closeEvent(self, event):
        self.keepalive_timer.stop()
        self.corner_timer.stop()
        self.tray.hide()
        save_config(self.cfg)
        event.accept()

def main():
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
