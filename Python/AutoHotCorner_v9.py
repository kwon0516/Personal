# -*- coding: utf-8 -*-
"""
AutoHotCorner v9 (PyQt5 single-file)
- Hotcorner detection: ALWAYS ON while app runs
- Keepalive: Start/Stop controls only periodic key
- Immediate key send on Keepalive start
- UI/UX: Dark theme, tabs, tray icon, live log
- Key capture dialog supports combos; CapsLock/NumLock supported
- Calibration dialog for precise corner points
- Settings: export/import/reset
- Autorun (Windows), Autostart keepalive, Auto-minimize to tray
- Window size option
- Cooldown (anti-repeat) option
NEW in v9:
  * "핫코너 ↦ 단축키 지정": 각 코너 행 오른쪽에 "사용" 체크박스 추가
  * "핫코너 ↦ 앱 실행" 섹션 추가: 각 코너별 경로 선택(찾기), 프로그램명 표시, "사용" 체크박스
  * 동일 코너에서 단축키/앱 실행 체크박스는 상호배타 (한쪽 On이면 다른쪽 Off)
  * 코너 트리거 시, 앱 실행이 켜져 있으면 앱 실행을 우선, 아니면 단축키 실행
"""

import os, sys, json, platform, subprocess
import pyautogui
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu, QLineEdit, QFileDialog, QTabWidget, QStyle, QDialog, QDialogButtonBox
)

# Windows registry for auto-run
if platform.system() == "Windows":
    try:
        import winreg
    except Exception:
        winreg = None
else:
    winreg = None

APP_NAME = "AutoHotCorner"
VERSION = "9.0"
ICON_NAME = "AutoHotKeyIcon.ico"  # provide this file next to the exe/py

# ----------------------------- Helpers -----------------------------

def resource_path(rel_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller (sys._MEIPASS)."""
    base = getattr(sys, "_MEIPASS", None)
    if base:  # PyInstaller bundle
        return os.path.join(base, rel_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), rel_path)

def default_config() -> dict:
    return {
        "selected_key": "f15",
        "cycle_min": 1,
        "use_monitor": [False, False],
        "hotkeys": [
            ["none","none","none"],
            ["none","none","none"],
            ["none","none","none"],
            ["none","none","none"],
        ],
        "hotkeys_enabled": [False, False, False, False],
        "apps_enabled":   [False, False, False, False],
        "apps_paths":     ["", "", "", ""],
        "calibration": [
            [["0","0"],["0","0"],["0","0"],["0","0"]],
            [["0","0"],["0","0"],["0","0"],["0","0"]],
        ],
        "tolerance_px": 0,
        # startup/UI options
        "autorun": False,
        "autostart_keepalive": False,
        "autominimize_tray": False,
        "window_size": [620, 510],
        # Cooldown
        "cooldown_ms": 500
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
            if not isinstance(data, dict): raise ValueError("bad cfg")
            # merge defaults to ensure new keys exist
            base = default_config()
            base.update(data)
            # Ensure list lengths
            for k in ("hotkeys_enabled","apps_enabled","apps_paths"):
                if len(base[k]) != 4:
                    if k == "apps_paths":
                        base[k] = (base[k] + ["","","",""])[:4]
                    else:
                        base[k] = [False,False,False,False]
            return base
        except Exception:
            pass
    return default_config()

def save_config(cfg: dict):
    try:
        config_path().write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to save config:", e)

# Windows autorun
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

def set_windows_autorun(enabled: bool):
    if platform.system() != "Windows" or winreg is None:
        return False, "Windows가 아니거나 winreg 사용 불가"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_ALL_ACCESS) as key:
            if enabled:
                exe_path = sys.executable
                # if running as script, try pythonw.exe + script path; on bundle use exe path
                if exe_path.lower().endswith("python.exe") or exe_path.lower().endswith("pythonw.exe"):
                    script = os.path.abspath(sys.argv[0])
                    cmd = f'"{exe_path}" "{script}"'
                else:
                    cmd = f'"{exe_path}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True, None
    except Exception as e:
        return False, str(e)

def get_windows_autorun() -> bool:
    if platform.system() != "Windows" or winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            _ = winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

# Key mapping
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
    try:
        for k in keys[:-1]:
            pyautogui.keyDown(k)
        pyautogui.press(keys[-1])
    finally:
        for k in reversed(keys[:-1]):
            try:
                pyautogui.keyUp(k)
            except Exception:
                pass

# ----------------------------- Modal dialogs -----------------------------

class KeyCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("키 입력")
        self.setModal(True)
        self.setFixedSize(360, 180)
        self.lbl = QLabel("조합키를 누른 뒤 Enter로 확정하거나, ESC로 취소하세요.\n예) Ctrl+Alt+K, Win+Shift+S")
        self.lbl.setAlignment(Qt.AlignCenter)

        self.lblPreview = QLabel("현재: (없음)")
        self.lblPreview.setAlignment(Qt.AlignCenter)
        self.lblPreview.setStyleSheet("color:#a8a8ad;")

        self._current = ["none"]

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addWidget(self.lbl)
        lay.addWidget(self.lblPreview)
        lay.addWidget(btns)

        self.setFocusPolicy(Qt.StrongFocus)

    @staticmethod
    def capture(parent=None):
        dlg = KeyCaptureDialog(parent)
        dlg.show(); dlg.activateWindow(); dlg.raise_(); dlg.setFocus()
        dlg.exec_()
        return getattr(dlg, "_result", ["none"])

    def _accept(self):
        self._result = self._current
        self.accept()

    def keyPressEvent(self, e):
        key = e.key()
        mods = e.modifiers()
        if key == Qt.Key_Escape:
            self._result = ["none"]
            self.reject()
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
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._result = self._current
            self.accept()
            return

        if key in qt_map:
            parts.append(qt_map[key])
        else:
            ch = e.text()
            if ch:
                parts.append(ch.lower())

        parts = [normalize_key(p) for p in parts if p]
        if not parts:
            parts = ["none"]
        parts = parts[:3]
        self._current = parts
        self.lblPreview.setText("현재: " + " + ".join(p.upper() for p in parts))

class CalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("좌표 보정")
        self.setModal(True)
        self.setFixedSize(380, 180)
        lay = QVBoxLayout(self)
        self.lbl = QLabel("원하는 위치에 마우스를 두고 Enter로 확정하세요.\n취소는 ESC")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lblPos = QLabel("현재: - , -")
        self.lblPos.setAlignment(Qt.AlignCenter)
        self.lblPos.setStyleSheet("color:#a8a8ad;")
        lay.addWidget(self.lbl)
        lay.addWidget(self.lblPos)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)

        self._pos = None
        self.setFocusPolicy(Qt.StrongFocus)

    def _tick(self):
        p = pyautogui.position()
        self.lblPos.setText(f"현재: {p.x} , {p.y}")

    @staticmethod
    def capture(parent=None):
        dlg = CalibrationDialog(parent)
        dlg.show(); dlg.activateWindow(); dlg.raise_(); dlg.setFocus()
        ok = dlg.exec_()
        return getattr(dlg, "_pos", None)

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
    background: transparent;
    selection-background-color: #3b5bd9;
    selection-color: white;
}
QTabWidget::pane { border: 1px solid #3c3c44; border-radius: 10px; }
QTabBar::tab {
    padding: 8px 14px; margin: 4px;
    border: 1px solid #444; border-radius: 8px;
}
QTabBar::tab:selected { background: #2a2a31; }
QMessageBox QLabel { color: black; }
QMessageBox { background: white; }
"""

def pill(text: str, ok: bool) -> str:
    color = "#1fbf75" if ok else "#d9534f"
    return f"<span style='background:{color};color:#fff;padding:3px 8px;border-radius:10px;'>{text}</span>"

# ----------------------------- Main Window -----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cfg = load_config()

        self.keepalive_running = False
        self._cooldown = False
        self._last_action = "-"

        pyautogui.FAILSAFE = False

        self.keepalive_timer = QTimer(self)
        self.keepalive_timer.timeout.connect(self._do_keepalive)

        self.corner_timer = QTimer(self)
        self.corner_timer.timeout.connect(self._poll_mouse)
        self.corner_timer.start(16)  # ALWAYS ON

        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        icon_path = resource_path(ICON_NAME)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Apply window size from config
        try:
            w, h = self.cfg.get("window_size", [620, 510])
            self.resize(int(w), int(h))
        except Exception:
            self.resize(620, 510)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setElideMode(Qt.ElideRight)
        self.setCentralWidget(tabs)

        # Keepalive Tab
        self.page_dash = QWidget()
        v = QVBoxLayout(self.page_dash); v.setSpacing(10)

        ctrl = QGroupBox("Keepalive (모니터 절전 방지)"); lay = QGridLayout(ctrl)
        self.btn_toggle = QPushButton("Keepalive Start")
        self.btn_toggle.setToolTip("주기(분)마다 선택한 키를 자동 전송합니다.")
        self.btn_toggle.clicked.connect(self.toggle_keepalive)

        self.combo_key = QComboBox(); self.combo_key.setEditable(True)
        for k in ["f15","scrolllock","shift","ctrl","alt","win","tab","enter","esc","space","capslock","numlock","none"]:
            self.combo_key.addItem(k)
        self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))

        self.spin_cycle = QSpinBox(); self.spin_cycle.setRange(1, 720)
        self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))

        self.btn_keepalive_now = QPushButton("즉시 실행")
        self.btn_keepalive_now.setToolTip("지금 즉시 주기 키를 2회 전송합니다.")
        self.btn_keepalive_now.clicked.connect(self._do_keepalive)

        self.lbl_status = QLabel(pill("Keepalive Off", False))
        self.lbl_recent = QLabel("최근 실행: -")
        self.lbl_recent.setStyleSheet("color:#a8a8ad;")

        lay.addWidget(QLabel("주기 키:"),0,0); lay.addWidget(self.combo_key,0,1)
        lay.addWidget(QLabel("주기(분):"),1,0); lay.addWidget(self.spin_cycle,1,1)
        lay.addWidget(self.btn_keepalive_now,0,2)
        lay.addWidget(self.lbl_status,0,3)
        lay.addWidget(self.btn_toggle,1,3)
        lay.addWidget(self.lbl_recent,3,0,1,4)
        v.addWidget(ctrl)

        # Info
        card2 = QGroupBox("실시간 이벤트 정보")
        ly2 = QGridLayout(card2)
        self.lbl_mouse = QLabel("마우스: -, -")
        self.lbl_tip = QLabel("코너에 마우스를 두면 등록된 동작(앱/단축키)이 실행됩니다.")
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

        # Hotkeys Tab
        self.page_hot = QWidget()
        v2 = QVBoxLayout(self.page_hot); v2.setSpacing(10)

        # === Hotkey mapping with per-corner enable ===
        gb = QGroupBox("핫코너 ↦ 단축키 지정"); gl = QGridLayout(gb)
        self.hotkey_btns = []   # [ [QPushButton x3] * 4 ]
        self.hotkey_enables = [] # [QCheckBox] * 4
        names = ["좌상(LT)","우상(RT)","좌하(LB)","우하(RB)"]
        for r in range(4):
            gl.addWidget(QLabel(names[r]), r, 0)
            row_btns = []
            for c in range(3):
                txt = self.cfg["hotkeys"][r][c].upper()
                b = QPushButton(txt)
                b.setObjectName(f"hk_{r}_{c}")
                b.setToolTip("클릭 후 원하는 키 조합을 입력 → Enter 또는 [확인]")
                b.clicked.connect(self._on_hotkey_assign)
                gl.addWidget(b, r, c+1)
                row_btns.append(b)
            chk = QCheckBox("사용")
            chk.setObjectName(f"hk_enable_{r}")
            chk.setChecked(bool(self.cfg["hotkeys_enabled"][r]))
            chk.stateChanged.connect(lambda _, rr=r: self._on_enable_changed(rr, mode='hotkey'))
            gl.addWidget(chk, r, 4)
            self.hotkey_btns.append(row_btns)
            self.hotkey_enables.append(chk)
        hint = QLabel("팁: Ctrl/Alt/Shift/Win + Key 조합을 지원합니다. 최대 3키.")
        hint.setStyleSheet("color:#aaaaae;")

        # === App execution with per-corner enable ===
        gb_app = QGroupBox("핫코너 ↦ 앱 실행"); gl2 = QGridLayout(gb_app)
        self.app_edits = []      # QLineEdit per corner
        self.app_browse = []     # QPushButton per corner
        self.app_name_labels = []# QLabel per corner
        self.app_enables = []    # QCheckBox per corner
        for r in range(4):
            gl2.addWidget(QLabel(names[r]), r, 0)
            edit = QLineEdit(self.cfg["apps_paths"][r])
            edit.setPlaceholderText("실행할 프로그램(또는 스크립트) 경로")
            edit.setObjectName(f"app_path_{r}")
            gl2.addWidget(edit, r, 1, 1, 2)
            btn = QPushButton("찾기")
            btn.setObjectName(f"app_browse_{r}")
            btn.clicked.connect(lambda _, rr=r: self._browse_app(rr))
            gl2.addWidget(btn, r, 3)
            lbl = QLabel(os.path.basename(self.cfg["apps_paths"][r]) if self.cfg["apps_paths"][r] else "(미선택)")
            lbl.setStyleSheet("color:#aaaaae;")
            lbl.setObjectName(f"app_name_{r}")
            gl2.addWidget(lbl, r, 4)
            chk = QCheckBox("사용")
            chk.setObjectName(f"app_enable_{r}")
            chk.setChecked(bool(self.cfg["apps_enabled"][r]))
            chk.stateChanged.connect(lambda _, rr=r: self._on_enable_changed(rr, mode='app'))
            gl2.addWidget(chk, r, 5)

            self.app_edits.append(edit)
            self.app_browse.append(btn)
            self.app_name_labels.append(lbl)
            self.app_enables.append(chk)

        v2.addWidget(gb); v2.addWidget(hint)
        v2.addWidget(gb_app); v2.addStretch(1)

        # Calibration Tab
        self.page_cal = QWidget()
        v3 = QVBoxLayout(self.page_cal); v3.setSpacing(10)
        gb2 = QGroupBox("코너 좌표 보정 & 사용 모니터"); glc = QGridLayout(gb2)

        self.chk_mon1 = QCheckBox("모니터 1 사용"); self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
        self.chk_mon2 = QCheckBox("모니터 2 사용"); self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))

        glc.addWidget(self.chk_mon1, 0, 0)
        glc.addWidget(self.chk_mon2, 0, 1)

        glc.addWidget(QLabel("허용 오차(px):"), 1, 0)
        self.tol_edit = QLineEdit(str(self.cfg.get("tolerance_px",0))); self.tol_edit.setFixedWidth(80)
        glc.addWidget(self.tol_edit, 1, 1)

        for mon in range(2):
            for idx, cname in enumerate(["LT","RT","LB","RB"]):
                x, y = self.cfg["calibration"][mon][idx]
                b = QPushButton(f"M{mon+1}-{cname}: {x}.{y}")
                b.setObjectName(f"cal_{mon}_{idx}")
                b.setToolTip("포인터를 원하는 위치로 옮긴 뒤 Enter (ESC 취소)")
                b.clicked.connect(self._start_calibration)
                glc.addWidget(b, 2+mon, idx)
        v3.addWidget(gb2)
        tip = QLabel("보정하지 않으면 (0,0) 등 기본 좌표로 인식됩니다.")
        tip.setStyleSheet("color:#aaaaae;")
        v3.addWidget(tip); v3.addStretch(1)

        # Settings Tab
        self.page_set = QWidget()
        v4 = QVBoxLayout(self.page_set); v4.setSpacing(10)
        gbs = QGroupBox("설정"); gls = QGridLayout(gbs)
        self.btn_save = QPushButton("저장"); self.btn_save.clicked.connect(self._save_clicked)
        self.btn_export = QPushButton("내보내기"); self.btn_export.clicked.connect(self._export_cfg)
        self.btn_import = QPushButton("가져오기"); self.btn_import.clicked.connect(self._import_cfg)
        self.btn_reset  = QPushButton("초기화"); self.btn_reset.clicked.connect(self._reset_cfg)

        # startup checkboxes
        self.chk_autorun = QCheckBox("Windows 시작 시 자동 실행")
        self.chk_autorun.setToolTip("로그인 시 자동으로 프로그램을 시작합니다. (현재 사용자)")
        self.chk_autorun.setChecked(bool(self.cfg.get("autorun", False) or get_windows_autorun()))

        self.chk_autostart_keepalive = QCheckBox("프로그램 시작 시 Keepalive 자동 시작")
        self.chk_autostart_keepalive.setChecked(bool(self.cfg.get("autostart_keepalive", False)))

        self.chk_autominimize = QCheckBox("프로그램 시작 시 트레이로 자동 최소화")
        self.chk_autominimize.setChecked(bool(self.cfg.get("autominimize_tray", False)))

        # window size controls
        ws = self.cfg.get("window_size", [620, 510])
        self.spin_win_w = QSpinBox(); self.spin_win_w.setRange(320, 4096); self.spin_win_w.setValue(int(ws[0]))
        self.spin_win_h = QSpinBox(); self.spin_win_h.setRange(240, 2160); self.spin_win_h.setValue(int(ws[1]))
        self.btn_apply_current_size = QPushButton("현재 창 크기 반영")
        self.btn_apply_current_size.setToolTip("현재 창 크기를 아래 W/H에 반영합니다.")
        self.btn_apply_current_size.clicked.connect(self._apply_current_window_size)

        # cooldown option
        self.spin_cooldown = QSpinBox(); self.spin_cooldown.setRange(0, 10000)
        self.spin_cooldown.setSingleStep(50)
        self.spin_cooldown.setSuffix(" ms")
        self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms", 500)))

        gls.addWidget(QLabel(f"설정 경로: {config_path()}"), 0, 0, 1, 4)
        gls.addWidget(self.btn_save, 1, 0)
        gls.addWidget(self.btn_export, 1, 1)
        gls.addWidget(self.btn_import, 1, 2)
        gls.addWidget(self.btn_reset, 1, 3)

        gls.addWidget(self.chk_autorun, 2, 0, 1, 2)
        gls.addWidget(self.chk_autostart_keepalive, 3, 0, 1, 2)
        gls.addWidget(self.chk_autominimize, 4, 0, 1, 2)

        gls.addWidget(QLabel("창 크기 W x H:"), 5, 0)
        gls.addWidget(self.spin_win_w, 5, 1)
        gls.addWidget(self.spin_win_h, 5, 2)
        gls.addWidget(self.btn_apply_current_size, 5, 3)

        gls.addWidget(QLabel("핫코너 연타 방지 딜레이:"), 6, 0)
        gls.addWidget(self.spin_cooldown, 6, 1)

        v4.addWidget(gbs)
        about = QGroupBox("About")
        ab_l = QVBoxLayout(about)
        self.lbl_about = QLabel(f"{APP_NAME} v{VERSION} — For Windows Hotcorner + Keepalive Monitor.")
        ab_l.addWidget(self.lbl_about)
        v4.addWidget(about); v4.addStretch(1)

        tabs.addTab(self.page_dash, "Keepalive")
        tabs.addTab(self.page_hot, "Hotcorners")
        tabs.addTab(self.page_cal, "Calibration")
        tabs.addTab(self.page_set, "Settings")

        # Tray
        self.tray = QSystemTrayIcon(self)
        tray_icon = None
        if os.path.exists(icon_path):
            tray_icon = QIcon(icon_path)
        if tray_icon is None or tray_icon.isNull():
            tray_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(tray_icon)
        self.tray.setToolTip("AutoHotCorner")
        m = QMenu()
        act_show = m.addAction("Show")
        act_hide = m.addAction("Hide")
        m.addSeparator()
        act_toggle = m.addAction("Keepalive Start/Stop")
        m.addSeparator()
        act_exit = m.addAction("Exit")
        act_show.triggered.connect(self.showNormal)
        act_hide.triggered.connect(self.hide)
        act_toggle.triggered.connect(self.toggle_keepalive)
        act_exit.triggered.connect(self.close)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

        self.setStyleSheet(CARD_QSS)

        # Apply startup options
        if self.chk_autorun.isChecked():
            ok, err = set_windows_autorun(True)
            if not ok and err:
                print("Autorun 설정 실패:", err)

        if self.chk_autominimize.isChecked():
            QTimer.singleShot(200, self._auto_minimize_to_tray)

        if self.chk_autostart_keepalive.isChecked():
            QTimer.singleShot(400, self.toggle_keepalive)

    # ----------------------------- Helpers -----------------------------
    def _apply_current_window_size(self):
        size = self.size()
        self.spin_win_w.setValue(size.width())
        self.spin_win_h.setValue(size.height())

    def _on_enable_changed(self, row: int, mode: str):
        """Mutual exclusivity between hotkey and app per corner."""
        if mode == 'hotkey':
            on = self.hotkey_enables[row].isChecked()
            if on:
                # disable app enable
                self.app_enables[row].setChecked(False)
            self.cfg["hotkeys_enabled"][row] = bool(on)
        else:
            on = self.app_enables[row].isChecked()
            if on:
                # disable hotkey enable
                self.hotkey_enables[row].setChecked(False)
            self.cfg["apps_enabled"][row] = bool(on)

    def _browse_app(self, row: int):
        path, _ = QFileDialog.getOpenFileName(self, "실행할 프로그램 선택", str(Path.home()))
        if not path:
            return
        self.app_edits[row].setText(path)
        self.app_name_labels[row].setText(os.path.basename(path) or "(미선택)")
        self.cfg["apps_paths"][row] = path

    # ----------------------------- Tray -----------------------------
    def _auto_minimize_to_tray(self):
        self.showMinimized()
        self.hide()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal(); self.raise_(); self.activateWindow()

    # ----------------------------- Log -----------------------------
    def _log(self, text):
        self._last_action = text
        self.lbl_recent.setText(f"최근 실행: {text}")

    # ----------------------------- Keepalive -----------------------------
    def toggle_keepalive(self):
        turn_on = not self.keepalive_running
        self.cfg["selected_key"] = normalize_key(self.combo_key.currentText())
        self.cfg["cycle_min"] = int(self.spin_cycle.value())

        if turn_on:
            key = self.cfg["selected_key"]
            ms = max(1, int(self.cfg["cycle_min"])) * 60_000
            self.keepalive_timer.stop()
            if key != "none":
                self.keepalive_timer.start(ms)
                self.keepalive_running = True
                self.lbl_status.setText(pill("Keepalive On", True))
                self._log(f"Keepalive 시작 ({key}, {self.cfg['cycle_min']}분)")
                self.btn_toggle.setText("Keepalive Stop")
                # Immediate send for user feedback
                self._do_keepalive()
            else:
                self._log("Keepalive 키가 'none'입니다. 키를 선택하세요.")
        else:
            self.keepalive_timer.stop()
            self.keepalive_running = False
            self.lbl_status.setText(pill("Keepalive Off", False))
            self._log("Keepalive 중지")
            self.btn_toggle.setText("Keepalive Start")

    def _do_keepalive(self):
        key = normalize_key(self.combo_key.currentText())
        if key == "none":
            self._log("주기 키: 사용 안함")
            return
        try:
            pyautogui.press(key); pyautogui.press(key)
            self._log(f"주기 키 전송: {key}")
        except Exception as e:
            self._log(f"주기 키 실패: {e}")

    # ----------------------------- Hotcorner detection (always on) -----------------------------
    def _poll_mouse(self):
        pos = pyautogui.position()
        self.lbl_mouse.setText(f"마우스: {pos.x}, {pos.y}")

        if self._cooldown:
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
                try:
                    checks[idx].append((0, int(ax), int(ay)))
                except Exception:
                    pass
        if use2:
            for idx in range(4):
                ax, ay = self.cfg["calibration"][1][idx]
                try:
                    checks[idx].append((1, int(ax), int(ay)))
                except Exception:
                    pass

        def match(ax, ay):
            if tol <= 0:
                return (curx == ax and cury == ay)
            return abs(curx-ax) <= tol and abs(cury-ay) <= tol

        for corner_idx, entries in checks.items():
            for mon, ax, ay in entries:
                if match(ax, ay):
                    self._trigger_corner(corner_idx)
                    self._cooldown = True
                    cooldown = int(self.spin_cooldown.value())
                    QTimer.singleShot(max(0, cooldown), lambda: setattr(self, "_cooldown", False))
                    return

    def _launch_app(self, path: str):
        try:
            if not path:
                raise RuntimeError("경로 없음")
            if platform.system() == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                # Fallback for non-Windows (rare for this project)
                subprocess.Popen([path])
            return True, None
        except Exception as e:
            return False, str(e)

    def _trigger_corner(self, idx: int):
        # 1) App execution has priority if enabled
        if self.app_enables[idx].isChecked():
            path = self.app_edits[idx].text().strip() or self.cfg["apps_paths"][idx]
            ok, err = self._launch_app(path)
            if ok:
                self._log(f"코너 {idx} 앱 실행: {os.path.basename(path) or path}")
            else:
                self._log(f"코너 {idx} 앱 실행 실패: {err}")
            return

        # 2) Hotkey combo if enabled
        if self.hotkey_enables[idx].isChecked():
            keys = [normalize_key(k) for k in self.cfg["hotkeys"][idx] if normalize_key(k) != "none"]
            if not keys:
                self._log(f"코너 {idx} 단축키 없음")
                return
            try:
                pyauto_press_combo(keys)
                self._log(f"코너 {idx} 실행: {'+'.join(k.upper() for k in keys)}")
            except Exception as e:
                self._log(f"코너 {idx} 실패: {e}")
            return

        # 3) Nothing enabled
        self._log(f"코너 {idx}: 동작이 비활성화되어 있습니다.")

    # ----------------------------- Handlers -----------------------------
    def _on_hotkey_assign(self):
        sender = self.sender()
        _, r, c = sender.objectName().split("_")
        r, c = int(r), int(c)

        keys_list = KeyCaptureDialog.capture(self)
        keys = [k for k in keys_list if k != "none"]
        while len(keys) < 3:
            keys.append("none")
        keys = keys[:3]
        self.cfg["hotkeys"][r] = keys
        for j, btn in enumerate(self.hotkey_btns[r]):
            btn.setText(self.cfg["hotkeys"][r][j].upper())
        self._log(f"코너 {r} 설정: {'+'.join([k.upper() for k in keys if k!='none']) or 'NONE'}")

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
        self._log(f"보정: M{mon+1}-{cname} = {x},{y}")

    # ----------------------------- Settings save/import/reset -----------------------------
    def _save_clicked(self):
        self.cfg["use_monitor"][0] = self.chk_mon1.isChecked()
        self.cfg["use_monitor"][1] = self.chk_mon2.isChecked()
        try:
            self.cfg["tolerance_px"] = max(0, int(self.tol_edit.text()))
        except Exception:
            self.cfg["tolerance_px"] = 0
        self.cfg["selected_key"] = normalize_key(self.combo_key.currentText())
        self.cfg["cycle_min"] = int(self.spin_cycle.value())

        # startup options
        self.cfg["autorun"] = self.chk_autorun.isChecked()
        self.cfg["autostart_keepalive"] = self.chk_autostart_keepalive.isChecked()
        self.cfg["autominimize_tray"] = self.chk_autominimize.isChecked()

        # UI options
        self.cfg["window_size"] = [int(self.spin_win_w.value()), int(self.spin_win_h.value())]

        # cooldown
        self.cfg["cooldown_ms"] = int(self.spin_cooldown.value())

        # hotkey/app enable+paths
        for r in range(4):
            self.cfg["hotkeys_enabled"][r] = self.hotkey_enables[r].isChecked()
            self.cfg["apps_enabled"][r] = self.app_enables[r].isChecked()
            self.cfg["apps_paths"][r] = self.app_edits[r].text().strip()

        if self.cfg["autorun"]:
            ok, err = set_windows_autorun(True)
            if not ok and err:
                QMessageBox.warning(self, "자동 실행 오류", f"자동 실행 설정에 실패했습니다:\n{err}")
        else:
            set_windows_autorun(False)

        save_config(self.cfg)

        # Apply immediately
        try:
            w, h = self.cfg["window_size"]
            self.resize(int(w), int(h))
        except Exception:
            pass

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
            base = default_config(); base.update(cfg)
            self.cfg = base

            # rebind UI
            self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))
            self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))
            self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
            self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))
            self.tol_edit.setText(str(self.cfg.get("tolerance_px",0)))

            self.chk_autorun.setChecked(bool(self.cfg.get("autorun", False) or get_windows_autorun()))
            self.chk_autostart_keepalive.setChecked(bool(self.cfg.get("autostart_keepalive", False)))
            self.chk_autominimize.setChecked(bool(self.cfg.get("autominimize_tray", False)))

            ws = self.cfg.get("window_size",[620,400])
            self.spin_win_w.setValue(int(ws[0])); self.spin_win_h.setValue(int(ws[1]))
            self.resize(int(ws[0]), int(ws[1]))

            self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms",500)))

            for r in range(4):
                for c in range(3):
                    self.hotkey_btns[r][c].setText(self.cfg["hotkeys"][r][c].upper())
                self.hotkey_enables[r].setChecked(bool(self.cfg["hotkeys_enabled"][r]))
                self.app_enables[r].setChecked(bool(self.cfg["apps_enabled"][r]))
                self.app_edits[r].setText(self.cfg["apps_paths"][r])
                self.app_name_labels[r].setText(os.path.basename(self.cfg["apps_paths"][r]) or "(미선택)")

            QMessageBox.information(self, "완료", "설정을 가져왔습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"가져오기 실패: {e}")

    def _reset_cfg(self):
        self.cfg = default_config()
        save_config(self.cfg)

        self.combo_key.setCurrentText(self.cfg["selected_key"])
        self.spin_cycle.setValue(self.cfg["cycle_min"])
        self.chk_mon1.setChecked(False); self.chk_mon2.setChecked(False)
        self.tol_edit.setText("0")
        self.chk_autorun.setChecked(False)
        self.chk_autostart_keepalive.setChecked(False)
        self.chk_autominimize.setChecked(False)

        ws = self.cfg.get("window_size",[620,400])
        self.spin_win_w.setValue(int(ws[0])); self.spin_win_h.setValue(int(ws[1]))
        self.resize(int(ws[0]), int(ws[1]))

        self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms",500)))

        for r in range(4):
            for c in range(3):
                self.hotkey_btns[r][c].setText("NONE")
            self.hotkey_enables[r].setChecked(False)
            self.app_enables[r].setChecked(False)
            self.app_edits[r].setText("")
            self.app_name_labels[r].setText("(미선택)")

        QMessageBox.information(self, "초기화", "설정을 초기화했습니다.")

    # ----------------------------- Window events -----------------------------
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
    icon_path = resource_path(ICON_NAME)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
