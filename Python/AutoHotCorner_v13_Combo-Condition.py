# -*- coding: utf-8 -*-
"""
AutoHotCorner v13
(see in-chat description for features)
"""
import os, sys, json, platform, subprocess, time
from pathlib import Path

import pyautogui
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QEasingCurve
from PyQt5.QtGui import QIcon, QPalette, QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu, QLineEdit, QFileDialog, QTabWidget, QStyle, QDialog,
    QDialogButtonBox, QColorDialog
)

APP_NAME="AutoHotCorner"; VERSION="13.0"; ICON_NAME="AutoHotKeyIcon.ico"

HAS_KB=False; KB=None
if platform.system()=="Windows":
    try:
        import keyboard as KB
        HAS_KB=True
    except Exception:
        KB=None; HAS_KB=False

if platform.system()=="Windows":
    try:
        import winreg
    except Exception:
        winreg=None
else:
    winreg=None

def resource_path(rel):
    base=getattr(sys,"_MEIPASS",None)
    return os.path.join(base if base else os.path.dirname(os.path.abspath(__file__)), rel)

def app_config_dir()->Path:
    if platform.system()=="Windows":
        base=os.getenv("APPDATA") or str(Path.home()/"AppData/Roaming")
        return Path(base)/APP_NAME
    return Path.home()/".config"/APP_NAME

def ensure_dir(p:Path): p.mkdir(parents=True, exist_ok=True)
def config_path()->Path: ensure_dir(app_config_dir()); return app_config_dir()/ "config.json"

SPECIAL_MAP={
"escape":"esc","esc":"esc","ctrl":"ctrl","control":"ctrl","alt":"alt","shift":"shift",
"win":"win","windows":"win","cmd":"win","meta":"win","super":"win",
"left":"left","right":"right","up":"up","down":"down",
"tab":"tab","capslock":"capslock","numlock":"numlock",
"f1":"f1","f2":"f2","f3":"f3","f4":"f4","f5":"f5","f6":"f6","f7":"f7","f8":"f8","f9":"f9","f10":"f10","f11":"f11","f12":"f12",
"enter":"enter","return":"enter","space":"space","backspace":"backspace","delete":"delete","home":"home","end":"end",
"pageup":"pageup","pagedown":"pagedown"
}
KB_SEND_MAP={"win":"windows"}
PYAUTO_MAP={"win":"winleft"}

def normalize_key(txt:str)->str:
    if not txt: return "none"
    s=txt.strip().lower()
    if s in SPECIAL_MAP: return SPECIAL_MAP[s]
    if len(s)==1: return s
    return s

def default_config():
    return {
        "selected_key":"f15","cycle_min":1,
        "use_monitor":[False,False],
        "hotkeys":[["none","none","none"] for _ in range(4)],
        "hotkeys_enabled":[False]*4,
        "apps_enabled":[False]*4,
        "apps_paths":[""]*4,
        "require_key_enabled":[False]*4,
        "require_key_name":["none"]*4,
        "calibration":[[["0","0"] for _ in range(4)] for __ in range(2)],
        "tolerance_px":0,
        "autorun":False,"autostart_keepalive":False,"autominimize_tray":False,
        "window_size":[620,720],
        "cooldown_ms":500,
        "effect_enabled":True,"effect_type":"Ripple","effect_size_px":120,
        "effect_duration_ms":450,"effect_color":"#5A82FF",
        "effect_stroke_px":4,"effect_stroke_opacity":60,"effect_fill_opacity":15
    }

def load_config():
    p=config_path()
    if p.exists():
        try:
            data=json.loads(p.read_text(encoding="utf-8"))
            base=default_config(); base.update(data)
            def fix_len(key, length, fill):
                arr=base.get(key,[])
                if len(arr)!=length: arr=(arr+[fill]*length)[:length]
                base[key]=arr
            fix_len("hotkeys_enabled",4,False)
            fix_len("apps_enabled",4,False)
            fix_len("apps_paths",4,"")
            if len(base.get("hotkeys",[]))!=4: base["hotkeys"]=default_config()["hotkeys"]
            fix_len("require_key_enabled",4,False)
            fix_len("require_key_name",4,"none")
            return base
        except Exception:
            pass
    return default_config()

def save_config(cfg): 
    try:
        config_path().write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("save_config error:", e)

RUN_KEY_PATH=r"Software\Microsoft\Windows\CurrentVersion\Run"
def set_windows_autorun(enabled:bool):
    if platform.system()!="Windows" or winreg is None: return False,"not windows"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_ALL_ACCESS) as key:
            if enabled:
                exe=sys.executable
                if exe.lower().endswith(("python.exe","pythonw.exe")):
                    script=os.path.abspath(sys.argv[0])
                    cmd=f'"{exe}" "{script}"'
                else: cmd=f'"{exe}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try: winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError: pass
        return True,None
    except Exception as e: return False,str(e)

def get_windows_autorun()->bool:
    if platform.system()!="Windows" or winreg is None: return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            _=winreg.QueryValueEx(key, APP_NAME); return True
    except FileNotFoundError: return False
    except Exception: return False

def _format_for_keyboard_lib(keys):
    parts=[]
    for k in keys: parts.append(KB_SEND_MAP.get(k,k))
    return "+".join(parts)

def pyauto_press_combo(keys):
    keys=[k for k in keys if k and k!="none"]
    if not keys: return
    try:
        if HAS_KB and KB is not None:
            KB.send(_format_for_keyboard_lib(keys), do_press=True, do_release=True); return
    except Exception as e:
        print("keyboard.send fail:", e)
    try:
        for k in keys[:-1]: pyautogui.keyDown(PYAUTO_MAP.get(k,k))
        pyautogui.press(PYAUTO_MAP.get(keys[-1], keys[-1]))
    finally:
        for k in reversed(keys[:-1]):
            try: pyautogui.keyUp(PYAUTO_MAP.get(k,k))
            except Exception: pass

def is_key_down_simple(name:str)->bool:
    k=KB_SEND_MAP.get(name,name)
    if not k or k=="none": return True
    if HAS_KB and KB is not None:
        try: return KB.is_pressed(k)
        except Exception: return False
    return False

from PyQt5.QtCore import QEvent
class KeyCaptureDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("키 입력"); self.setModal(True); self.setFixedSize(440,210)
        self.lbl=QLabel("조합키를 누르고 Enter로 확정, ESC로 취소 (최대 3키)"); self.lbl.setAlignment(Qt.AlignCenter)
        self.lblPreview=QLabel("현재: (없음)"); self.lblPreview.setAlignment(Qt.AlignCenter); self.lblPreview.setStyleSheet("color:#a8a8ad;")
        self._current=["none"]; self._last_non_empty=["none"]; self._max_combo=["none"]; self._pressing=False; self._down_order=[]; self._result=["none"]
        btns=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(self._accept); btns.rejected.connect(self.reject)
        lay=QVBoxLayout(self); lay.addWidget(self.lbl); lay.addWidget(self.lblPreview); lay.addWidget(btns)
        self.setFocusPolicy(Qt.StrongFocus)
        self._use_kb_hook=bool(HAS_KB and KB is not None and platform.system()=="Windows"); self._pressed=set(); self._hook=None
    def showEvent(self,e):
        super().showEvent(e)
        if self._use_kb_hook and self._hook is None:
            def _handler(ev):
                try:
                    name=(ev.name or "").lower()
                    if name in ("left windows","right windows"): name="win"
                    name=SPECIAL_MAP.get(name,name)
                    if ev.event_type=="down":
                        if name in ("enter","return"):
                            seq=[k for k in self._down_order if k and k!="none"][:3]
                            if not seq: seq=self._max_combo if self._max_combo!=["none"] else self._last_non_empty
                            self._result=seq; self.accept(); return
                        if name in ("esc","escape"): self._result=["none"]; self.reject(); return
                        if name and name!="none": self._pressed.add(name)
                    elif ev.event_type=="up":
                        if name in self._pressed: self._pressed.discard(name)
                    mods=[m for m in ("ctrl","alt","shift","win") if m in self._pressed]
                    mains=[k for k in self._pressed if k not in ("ctrl","alt","shift","win")]
                    seq_now=(mods + (mains[-1:] if mains else []))[:3]
                    if not seq_now: seq_now=["none"]
                    if ev.event_type=="down":
                        if not self._pressing:
                            self._pressing=True; self._max_combo=["none"]; self._down_order=[]
                        if seq_now!=["none"]:
                            self._last_non_empty=seq_now
                            k=name
                            if k not in self._down_order and k not in ("enter","return","esc","escape"): self._down_order.append(k)
                            def score(s):
                                base=len([x for x in s if x!="none"]); has_main=any(x not in ("ctrl","alt","shift","win") for x in s)
                                return base + (2 if has_main else 0)
                            if score(seq_now)>score(self._max_combo): self._max_combo=seq_now
                    self._current=seq_now
                    if self._pressed:
                        preview=self._max_combo if self._max_combo!=["none"] else self._last_non_empty
                        self.lblPreview.setText("현재: " + " + ".join(p.upper() for p in preview))
                    else:
                        if self._pressing:
                            final=self._max_combo if self._max_combo!=["none"] else self._last_non_empty
                            self.lblPreview.setText("현재: " + " + ".join(p.upper() for p in final))
                            self._current=final; self._pressing=False
                        else:
                            self.lblPreview.setText("현재: (없음)")
                except Exception:
                    pass
            try: self._hook=KB.hook(_handler, suppress=True)
            except Exception: self._use_kb_hook=False
    @staticmethod
    def capture(parent=None):
        dlg=KeyCaptureDialog(parent); dlg.show(); dlg.activateWindow(); dlg.raise_(); dlg.setFocus(); dlg.exec_(); dlg._cleanup_hook(); return getattr(dlg,"_result",["none"])
    def _cleanup_hook(self):
        if self._hook is not None:
            try: KB.unhook(self._hook)
            except Exception: pass
            self._hook=None
    def _accept(self):
        seq=[k for k in getattr(self,"_down_order",[]) if k and k!="none"][:3]
        if not seq:
            seq=self._current
            if seq==["none"]: seq=self._last_non_empty
        self._result=seq; self.accept()
    def keyPressEvent(self,e):
        if self._use_kb_hook: return
        key=e.key(); mods=e.modifiers()
        if key==Qt.Key_Escape: self._result=["none"]; self.reject(); return
        if key in (Qt.Key_Return, Qt.Key_Enter): self._result=self._current; self.accept(); return
        parts=[]
        if mods & Qt.ControlModifier: parts.append("ctrl")
        if mods & Qt.AltModifier: parts.append("alt")
        if mods & Qt.ShiftModifier: parts.append("shift")
        if mods & Qt.MetaModifier: parts.append("win")
        qt_map={
            Qt.Key_Left:"left",Qt.Key_Right:"right",Qt.Key_Up:"up",Qt.Key_Down:"down",
            Qt.Key_Tab:"tab",Qt.Key_CapsLock:"capslock",Qt.Key_NumLock:"numlock",
            Qt.Key_F1:"f1",Qt.Key_F2:"f2",Qt.Key_F3:"f3",Qt.Key_F4:"f4",Qt.Key_F5:"f5",Qt.Key_F6:"f6",
            Qt.Key_F7:"f7",Qt.Key_F8:"f8",Qt.Key_F9:"f9",Qt.Key_F10:"f10",Qt.Key_F11:"f11",Qt.Key_F12:"f12",
            Qt.Key_Return:"enter",Qt.Key_Enter:"enter",Qt.Key_Backspace:"backspace",Qt.Key_Delete:"delete",
            Qt.Key_Home:"home",Qt.Key_End:"end",Qt.Key_PageUp:"pageup",Qt.Key_PageDown:"pagedown",Qt.Key_Space:"space",
        }
        if key in qt_map: parts.append(qt_map[key])
        else:
            ch=e.text()
            if ch: parts.append(ch.lower())
        parts=[normalize_key(p) for p in parts if p]
        if not parts: parts=["none"]
        parts=parts[:3]; self._current=parts; self.lblPreview.setText("현재: " + " + ".join(p.upper() for p in parts))
    def closeEvent(self,e): self._cleanup_hook(); super().closeEvent(e)

class EffectOverlay(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._center=QPoint(0,0); self._radius=0; self._max_radius=120; self._opacity=0.0
        self._timer=QTimer(self); self._timer.timeout.connect(self._tick)
        self._duration_ms=450; self._elapsed=0; self._last_ms=None; self._hold=False
        self._effect_type="Ripple"; self._color=QColor("#5A82FF")
        self._stroke_px=4; self._stroke_alpha=0.6; self._fill_alpha=0.15
        rec=QApplication.desktop().geometry(); self.setGeometry(rec); self.hide()
    def configure(self,*,effect_type,max_radius,duration_ms,color,stroke_px,stroke_opacity_percent,fill_opacity_percent):
        self._effect_type=effect_type; self._max_radius=max(20,int(max_radius)); self._duration_ms=max(100,int(duration_ms))
        self._color=color; self._stroke_px=max(1,int(stroke_px))
        self._stroke_alpha=max(0,min(100,int(stroke_opacity_percent)))/100.0
        self._fill_alpha=max(0,min(100,int(fill_opacity_percent)))/100.0
    def show_effect(self,x,y,hold=False):
        self._center=QPoint(int(x),int(y)); self._radius=0; self._opacity=1.0
        self._elapsed=0; self._last_ms=int(time.time()*1000); self._hold=bool(hold)
        self.show(); self.raise_(); self._timer.start(16)
    def hide_effect(self): self._timer.stop(); self.hide()
    def _tick(self):
        now=int(time.time()*1000)
        if self._last_ms is None: self._last_ms=now
        delta=now-self._last_ms; self._last_ms=now; self._elapsed+=delta
        t=min(1.0, self._elapsed/float(self._duration_ms))
        eased=QEasingCurve(QEasingCurve.OutCubic).valueForProgress(t)
        if not self._hold:
            self._radius=int(self._max_radius*eased); self._opacity=max(0.0, 1.0-t)
        else:
            if t<1.0: self._radius=int(self._max_radius*eased)
            else: self._radius=int(self._max_radius)
            self._opacity=1.0
        self.update()
        if t>=1.0 and not self._hold: self._timer.stop(); self.hide()
    def paintEvent(self,ev):
        if self._opacity<=0.0: return
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing,True)
        stroke_col=QColor(self._color.red(), self._color.green(), self._color.blue(), int(255*self._opacity*self._stroke_alpha))
        fill_col=QColor(self._color.red(), self._color.green(), self._color.blue(), int(255*self._opacity*self._fill_alpha))
        if self._effect_type=="Ripple":
            pen=QPen(stroke_col, self._stroke_px); p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawEllipse(self._center, self._radius, self._radius)
            p.setPen(Qt.NoPen); p.setBrush(QBrush(fill_col))
            inner=max(0, self._radius-max(8, self._stroke_px*2)); p.drawEllipse(self._center, inner, inner)
        elif self._effect_type=="SquareRipple":
            pen=QPen(stroke_col, self._stroke_px); p.setPen(pen); p.setBrush(Qt.NoBrush)
            side=self._radius*2; rect=QRect(self._center.x()-self._radius, self._center.y()-self._radius, side, side); p.drawRect(rect)
            p.setPen(Qt.NoPen); p.setBrush(QBrush(fill_col))
            inset=max(0, self._stroke_px*2); rect2=QRect(rect.adjusted(inset,inset,-inset,-inset)); p.drawRect(rect2)
        elif self._effect_type=="Flash":
            pen=QPen(Qt.NoPen); p.setPen(pen); p.setBrush(QBrush(fill_col))
            size=max(20,int(self._radius*1.2)); pts=[QPoint(self._center.x(),self._center.y()-size),
                QPoint(self._center.x()+size,self._center.y()), QPoint(self._center.x(),self._center.y()+size), QPoint(self._center.x()-size,self._center.y())]
            p.drawPolygon(*pts); pen2=QPen(stroke_col, self._stroke_px); p.setPen(pen2); p.setBrush(Qt.NoBrush); p.drawPolygon(*pts)
        elif self._effect_type=="Crosshair":
            pen=QPen(stroke_col, self._stroke_px); p.setPen(pen); p.setBrush(Qt.NoBrush); r=self._radius
            p.drawLine(self._center.x()-r, self._center.y(), self._center.x()+r, self._center.y())
            p.drawLine(self._center.x(), self._center.y()-r, self._center.x(), self._center.y()+r)
            p.setPen(Qt.NoPen); p.setBrush(QBrush(fill_col)); p.drawEllipse(self._center, max(2,self._stroke_px), max(2,self._stroke_px))

def apply_dark_theme(app):
    pal=QPalette(); base=QColor(30,30,33); alt=QColor(40,40,45); text=QColor(230,230,235); acc=QColor(90,130,255)
    pal.setColor(QPalette.Window, base); pal.setColor(QPalette.WindowText, text)
    pal.setColor(QPalette.Base, alt); pal.setColor(QPalette.AlternateBase, base)
    pal.setColor(QPalette.Text, text); pal.setColor(QPalette.Button, alt); pal.setColor(QPalette.ButtonText, text)
    pal.setColor(QPalette.Highlight, acc); pal.setColor(QPalette.HighlightedText, QColor(255,255,255))
    app.setPalette(pal)

CARD_QSS="""
QGroupBox { font-weight:600; border:1px solid #3c3c44; border-radius:12px; margin-top:14px; padding:10px; }
QGroupBox::title { subcontrol-origin: margin; left:10px; padding:0 6px; }
QPushButton { padding:10px 14px; border-radius:10px; border:1px solid #555; }
QPushButton:hover { background:#2f2f36; } QPushButton:pressed { background:#27272e; }
QLineEdit, QSpinBox, QComboBox { padding:8px 10px; border-radius:8px; border:1px solid #555; background:transparent; }
QTabWidget::pane { border:1px solid #3c3c44; border-radius:10px; } 
QTabBar::tab { padding:8px 14px; margin:4px; border:1px solid #444; border-radius:8px; }
QTabBar::tab:selected { background:#2a2a31; }
QMessageBox QLabel { color:black; } QMessageBox { background:white; }
"""
def pill(text,ok): color="#1fbf75" if ok else "#d9534f"; return f"<span style='background:{color};color:#fff;padding:3px 8px;border-radius:10px;'>{text}</span>"

class CalibrationDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("좌표 보정"); self.setModal(True); self.setFixedSize(380,180)
        lay=QVBoxLayout(self); self.lbl=QLabel("원하는 위치에 마우스를 두고 Enter로 확정 (ESC 취소)"); self.lbl.setAlignment(Qt.AlignCenter)
        self.lblPos=QLabel("현재: - , -"); self.lblPos.setAlignment(Qt.AlignCenter); self.lblPos.setStyleSheet("color:#a8a8ad;")
        lay.addWidget(self.lbl); lay.addWidget(self.lblPos)
        self.timer=QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(60)
        self._pos=None; self.setFocusPolicy(Qt.StrongFocus)
    def _tick(self):
        p=pyautogui.position(); self.lblPos.setText(f"현재: {p.x} , {p.y}")
    @staticmethod
    def capture(parent=None):
        dlg=CalibrationDialog(parent); dlg.show(); dlg.activateWindow(); dlg.raise_(); dlg.setFocus()
        ok=dlg.exec_(); return getattr(dlg,"_pos",None)
    def keyPressEvent(self,e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            p=pyautogui.position(); self._pos=(str(p.x),str(p.y)); self.accept()
        elif e.key()==Qt.Key_Escape: self._pos=None; self.reject()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg=load_config()
        self.keepalive_running=False; self._cooldown=False; self._last_action="-"
        self._inside_idx=None; self._inside_visual=None
        pyautogui.FAILSAFE=False
        self.keepalive_timer=QTimer(self); self.keepalive_timer.timeout.connect(self._do_keepalive)
        self.corner_timer=QTimer(self); self.corner_timer.timeout.connect(self._poll_mouse); self.corner_timer.start(16)

        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        icon_path=resource_path(ICON_NAME)
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        try: w,h=self.cfg.get("window_size",[620,720]); self.resize(int(w),int(h))
        except Exception: self.resize(620,720)

        tabs=QTabWidget(); tabs.setDocumentMode(True); tabs.setElideMode(Qt.ElideRight); self.setCentralWidget(tabs)

        # Keepalive
        self.page_dash=QWidget(); v=QVBoxLayout(self.page_dash)
        ctrl=QGroupBox("Keepalive (모니터 절전 방지)"); lay=QGridLayout(ctrl)
        self.btn_toggle=QPushButton("Keepalive Start"); self.btn_toggle.clicked.connect(self.toggle_keepalive)
        self.combo_key=QComboBox(); self.combo_key.setEditable(True)
        for k in ["f15","scrolllock","shift","ctrl","alt","win","tab","enter","esc","space","capslock","numlock","none"]: self.combo_key.addItem(k)
        self.combo_key.setCurrentText(self.cfg.get("selected_key","f15"))
        self.spin_cycle=QSpinBox(); self.spin_cycle.setRange(1,720); self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))
        self.btn_keepalive_now=QPushButton("즉시 실행"); self.btn_keepalive_now.clicked.connect(self._do_keepalive)
        self.lbl_status=QLabel(pill("Keepalive Off",False)); self.lbl_recent=QLabel("최근 실행: -"); self.lbl_recent.setStyleSheet("color:#a8a8ad;")
        lay.addWidget(QLabel("주기 키:"),0,0); lay.addWidget(self.combo_key,0,1); lay.addWidget(self.btn_keepalive_now,0,2); lay.addWidget(self.lbl_status,0,3)
        lay.addWidget(QLabel("주기(분):"),1,0); lay.addWidget(self.spin_cycle,1,1); lay.addWidget(self.btn_toggle,1,3); lay.addWidget(self.lbl_recent,3,0,1,4)
        v.addWidget(ctrl)
        card2=QGroupBox("실시간 이벤트 정보"); ly2=QGridLayout(card2)
        self.lbl_mouse=QLabel("마우스: -, -"); self.lbl_tip=QLabel("코너에 마우스를 두면 효과가 나타나고, 벗어나면 실행합니다."); self.lbl_tip.setStyleSheet("color:#aaaaae;")
        ly2.addWidget(self.lbl_mouse,0,0); ly2.addWidget(self.lbl_tip,1,0); v.addWidget(card2)
        card3=QGroupBox("빠른 테스트"); ly3=QHBoxLayout(card3)
        for i,name in enumerate(["LT","RT","LB","RB"]):
            b=QPushButton(f"{name} 실행(강제)"); b.clicked.connect(lambda _,idx=i:self._trigger_corner(idx)); ly3.addWidget(b)
        v.addWidget(card3); v.addStretch(1)

        # Hotcorners tab
        self.page_hot=QWidget(); v2=QVBoxLayout(self.page_hot)
        gb=QGroupBox("핫코너 ↦ 단축키 지정"); gl=QGridLayout(gb)
        self.hotkey_btns=[]; self.hotkey_enables=[]; names=["좌상(LT)","우상(RT)","좌하(LB)","우하(RB)"]
        for r in range(4):
            gl.addWidget(QLabel(names[r]), r, 0)
            row_btns=[]
            for c in range(3):
                txt=self.cfg["hotkeys"][r][c].upper()
                b=QPushButton(txt); b.setObjectName(f"hk_{r}_{c}"); b.clicked.connect(self._on_hotkey_assign); gl.addWidget(b, r, c+1); row_btns.append(b)
            chk=QCheckBox("사용"); chk.setObjectName(f"hk_enable_{r}"); chk.setChecked(bool(self.cfg["hotkeys_enabled"][r]))
            chk.stateChanged.connect(lambda _,rr=r:self._on_enable_changed(rr,'hotkey')); gl.addWidget(chk, r, 4)
            self.hotkey_btns.append(row_btns); self.hotkey_enables.append(chk)
        hint=QLabel("팁: Ctrl/Alt/Shift/Win + Key 조합 지원 (Win+Tab 등)"); hint.setStyleSheet("color:#aaaaae;")

        gb_app=QGroupBox("핫코너 ↦ 앱 실행"); gl2=QGridLayout(gb_app)
        self.app_edits=[]; self.app_browse=[]; self.app_name_labels=[]; self.app_enables=[]
        for r in range(4):
            gl2.addWidget(QLabel(names[r]), r, 0)
            edit=QLineEdit(self.cfg["apps_paths"][r]); edit.setPlaceholderText("실행 파일(또는 스크립트) 경로"); edit.setObjectName(f"app_path_{r}")
            gl2.addWidget(edit, r, 1, 1, 2)
            btn=QPushButton("찾기"); btn.setObjectName(f"app_browse_{r}"); btn.clicked.connect(lambda _,rr=r:self._browse_app(rr)); gl2.addWidget(btn, r, 3)
            lbl=QLabel(os.path.basename(self.cfg["apps_paths"][r]) if self.cfg["apps_paths"][r] else "(미선택)"); lbl.setStyleSheet("color:#aaaaae;"); lbl.setObjectName(f"app_name_{r}")
            gl2.addWidget(lbl, r, 4)
            chk=QCheckBox("사용"); chk.setObjectName(f"app_enable_{r}"); chk.setChecked(bool(self.cfg["apps_enabled"][r]))
            chk.stateChanged.connect(lambda _,rr=r:self._on_enable_changed(rr,'app')); gl2.addWidget(chk, r, 5)
            self.app_edits.append(edit); self.app_browse.append(btn); self.app_name_labels.append(lbl); self.app_enables.append(chk)

        gb_req=QGroupBox("핫코너 ↦ 조건 키(누른 상태일 때만 실행)"); gl3=QGridLayout(gb_req)
        self.req_enables=[]; self.req_combos=[]
        req_keys=["none","ctrl","alt","shift","win","tab","esc","space","enter"]+[f"f{i}" for i in range(1,13)]+list("abcdefghijklmnopqrstuvwxyz")
        for r in range(4):
            gl3.addWidget(QLabel(names[r]), r, 0)
            chk=QCheckBox("키 Down 상태일 때만"); chk.setChecked(bool(self.cfg["require_key_enabled"][r])); chk.setToolTip("지정 키를 누르고 있어야 실행합니다.")
            combo=QComboBox(); combo.setEditable(True)
            for k in req_keys: combo.addItem(k)
            combo.setCurrentText(self.cfg["require_key_name"][r])
            gl3.addWidget(chk, r, 1); gl3.addWidget(QLabel("키:"), r, 2); gl3.addWidget(combo, r, 3)
            self.req_enables.append(chk); self.req_combos.append(combo)

        v2.addWidget(gb); v2.addWidget(hint); v2.addWidget(gb_app); v2.addWidget(gb_req); v2.addStretch(1)

        # Calibration
        self.page_cal=QWidget(); v3=QVBoxLayout(self.page_cal)
        gb2=QGroupBox("코너 좌표 보정 & 사용 모니터"); glc=QGridLayout(gb2)
        self.chk_mon1=QCheckBox("모니터 1 사용"); self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0]))
        self.chk_mon2=QCheckBox("모니터 2 사용"); self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1]))
        glc.addWidget(self.chk_mon1,0,0); glc.addWidget(self.chk_mon2,0,1)
        glc.addWidget(QLabel("허용 오차(px):"),1,0); self.tol_edit=QLineEdit(str(self.cfg.get("tolerance_px",0))); self.tol_edit.setFixedWidth(80); glc.addWidget(self.tol_edit,1,1)
        for mon in range(2):
            for idx,cname in enumerate(["LT","RT","LB","RB"]):
                x,y=self.cfg["calibration"][mon][idx]; b=QPushButton(f"M{mon+1}-{cname}: {x}.{y}"); b.setObjectName(f"cal_{mon}_{idx}")
                b.clicked.connect(self._start_calibration); glc.addWidget(b, 2+mon, idx)
        v3.addWidget(gb2); tip=QLabel("보정하지 않으면 (0,0) 등 기본 좌표로 인식됩니다."); tip.setStyleSheet("color:#aaaaae;"); v3.addWidget(tip); v3.addStretch(1)

        # Settings
        self.page_set=QWidget(); v4=QVBoxLayout(self.page_set)
        gbs=QGroupBox("설정"); gls=QGridLayout(gbs)
        self.btn_save=QPushButton("저장"); self.btn_save.clicked.connect(self._save_clicked)
        self.btn_export=QPushButton("내보내기"); self.btn_export.clicked.connect(self._export_cfg)
        self.btn_import=QPushButton("가져오기"); self.btn_import.clicked.connect(self._import_cfg)
        self.btn_reset=QPushButton("초기화"); self.btn_reset.clicked.connect(self._reset_cfg)
        self.chk_autorun=QCheckBox("Windows 시작 시 자동 실행"); self.chk_autorun.setChecked(bool(self.cfg.get("autorun",False) or get_windows_autorun()))
        self.chk_autostart_keepalive=QCheckBox("프로그램 시작 시 Keepalive 자동 시작"); self.chk_autostart_keepalive.setChecked(bool(self.cfg.get("autostart_keepalive",False)))
        self.chk_autominimize=QCheckBox("프로그램 시작 시 트레이로 자동 최소화"); self.chk_autominimize.setChecked(bool(self.cfg.get("autominimize_tray",False)))
        ws=self.cfg.get("window_size",[620,720]); self.spin_win_w=QSpinBox(); self.spin_win_w.setRange(320,4096); self.spin_win_w.setValue(int(ws[0]))
        self.spin_win_h=QSpinBox(); self.spin_win_h.setRange(240,2160); self.spin_win_h.setValue(int(ws[1]))
        self.btn_apply_current_size=QPushButton("현재 창 크기 반영"); self.btn_apply_current_size.clicked.connect(self._apply_current_window_size)
        self.spin_cooldown=QSpinBox(); self.spin_cooldown.setRange(0,10000); self.spin_cooldown.setSingleStep(50); self.spin_cooldown.setSuffix(" ms"); self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms",500)))

        gb_effect=QGroupBox("핫코너 시각 효과"); ge=QGridLayout(gb_effect)
        self.chk_effect=QCheckBox("효과 사용"); self.chk_effect.setChecked(bool(self.cfg.get("effect_enabled",True)))
        self.combo_effect=QComboBox(); [self.combo_effect.addItem(n) for n in ["Ripple","SquareRipple","Flash","Crosshair"]]; self.combo_effect.setCurrentText(self.cfg.get("effect_type","Ripple"))
        self.spin_effect_size=QSpinBox(); self.spin_effect_size.setRange(20,1200); self.spin_effect_size.setValue(int(self.cfg.get("effect_size_px",120))); self.spin_effect_size.setSuffix(" px")
        self.spin_effect_dur=QSpinBox(); self.spin_effect_dur.setRange(100,5000); self.spin_effect_dur.setValue(int(self.cfg.get("effect_duration_ms",450))); self.spin_effect_dur.setSuffix(" ms")
        self.spin_effect_stroke=QSpinBox(); self.spin_effect_stroke.setRange(1,30); self.spin_effect_stroke.setValue(int(self.cfg.get("effect_stroke_px",4))); self.spin_effect_stroke.setSuffix(" px")
        self.spin_effect_stroke_op=QSpinBox(); self.spin_effect_stroke_op.setRange(0,100); self.spin_effect_stroke_op.setValue(int(self.cfg.get("effect_stroke_opacity",60))); self.spin_effect_stroke_op.setSuffix(" %")
        self.spin_effect_fill_op=QSpinBox(); self.spin_effect_fill_op.setRange(0,100); self.spin_effect_fill_op.setValue(int(self.cfg.get("effect_fill_opacity",15))); self.spin_effect_fill_op.setSuffix(" %")
        self.btn_pick_color=QPushButton("색상 선택"); self.lbl_color_preview=QLabel("■"); self.lbl_color_preview.setFixedWidth(22); self.lbl_color_preview.setAlignment(Qt.AlignCenter)
        self._effect_color=QColor(self.cfg.get("effect_color","#5A82FF")); self._update_color_preview(); self.btn_pick_color.clicked.connect(self._pick_color)
        ge.addWidget(self.chk_effect,0,0)
        ge.addWidget(QLabel("종류:"),1,0); ge.addWidget(self.combo_effect,1,1)
        ge.addWidget(QLabel("크기:"),2,0); ge.addWidget(self.spin_effect_size,2,1)
        ge.addWidget(QLabel("지속시간:"),2,2); ge.addWidget(self.spin_effect_dur,2,3)
        ge.addWidget(QLabel("선 두께:"),3,0); ge.addWidget(self.spin_effect_stroke,3,1)
        ge.addWidget(QLabel("선 불투명도:"),3,2); ge.addWidget(self.spin_effect_stroke_op,3,3)
        ge.addWidget(QLabel("면 불투명도:"),4,0); ge.addWidget(self.spin_effect_fill_op,4,1)
        ge.addWidget(self.btn_pick_color,4,2); ge.addWidget(self.lbl_color_preview,4,3)

        gls.addWidget(QLabel(f"설정 경로: {config_path()}"),0,0,1,4)
        gls.addWidget(self.btn_save,1,0); gls.addWidget(self.btn_export,1,1); gls.addWidget(self.btn_import,1,2); gls.addWidget(self.btn_reset,1,3)
        gls.addWidget(self.chk_autorun,2,0,1,2); gls.addWidget(self.chk_autostart_keepalive,3,0,1,2); gls.addWidget(self.chk_autominimize,4,0,1,2)
        gls.addWidget(QLabel("창 크기 W x H:"),5,0); gls.addWidget(self.spin_win_w,5,1); gls.addWidget(self.spin_win_h,5,2); gls.addWidget(self.btn_apply_current_size,5,3)
        gls.addWidget(QLabel("핫코너 연타 방지 딜레이:"),6,0); gls.addWidget(self.spin_cooldown,6,1)
        gls.addWidget(gb_effect,7,0,1,4)
        v4.addWidget(gbs); about=QGroupBox("About"); ab_l=QVBoxLayout(about); self.lbl_about=QLabel(f"{APP_NAME} v{VERSION} — Windows Hotcorner + Keepalive"); ab_l.addWidget(self.lbl_about); v4.addWidget(about); v4.addStretch(1)

        tabs.addTab(self.page_dash,"Keepalive"); tabs.addTab(self.page_hot,"Hotcorners"); tabs.addTab(self.page_cal,"Calibration"); tabs.addTab(self.page_set,"Settings")
        self.tray=QSystemTrayIcon(self); tray_icon=QIcon(icon_path) if os.path.exists(icon_path) else self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(tray_icon); self.tray.setToolTip("AutoHotCorner")
        m=QMenu(); a_show=m.addAction("Show"); a_hide=m.addAction("Hide"); m.addSeparator(); a_tog=m.addAction("Keepalive Start/Stop"); m.addSeparator(); a_exit=m.addAction("Exit")
        a_show.triggered.connect(self.showNormal); a_hide.triggered.connect(self.hide); a_tog.triggered.connect(self.toggle_keepalive); a_exit.triggered.connect(self.close)
        self.tray.setContextMenu(m); self.tray.activated.connect(self._tray_activated); self.tray.show()
        self.setStyleSheet(CARD_QSS)
        self.overlay=EffectOverlay()

        if self.chk_autominimize.isChecked(): QTimer.singleShot(200, self._auto_minimize_to_tray)
        if self.chk_autostart_keepalive.isChecked(): QTimer.singleShot(400, self.toggle_keepalive)

    def _update_color_preview(self):
        c=getattr(self,"_effect_color",QColor("#5A82FF")); self.lbl_color_preview.setStyleSheet(f"font-size:18px;color:{c.name()};")
    def _pick_color(self):
        c=QColorDialog.getColor(getattr(self,"_effect_color",QColor("#5A82FF")), self, "효과 색상 선택")
        if c.isValid(): self._effect_color=c; self._update_color_preview()
    def _apply_current_window_size(self):
        s=self.size(); self.spin_win_w.setValue(s.width()); self.spin_win_h.setValue(s.height())
    def _on_enable_changed(self,row,mode):
        if mode=='hotkey':
            on=self.hotkey_enables[row].isChecked()
            if on: self.app_enables[row].setChecked(False)
            self.cfg["hotkeys_enabled"][row]=bool(on)
        else:
            on=self.app_enables[row].isChecked()
            if on: self.hotkey_enables[row].setChecked(False)
            self.cfg["apps_enabled"][row]=bool(on)
    def _browse_app(self,row):
        path,_=QFileDialog.getOpenFileName(self,"실행할 프로그램 선택",str(Path.home()))
        if not path: return
        self.app_edits[row].setText(path); self.app_name_labels[row].setText(os.path.basename(path) or "(미선택)"); self.cfg["apps_paths"][row]=path
    def _auto_minimize_to_tray(self): self.showMinimized(); self.hide()
    def _tray_activated(self,reason):
        if reason==QSystemTrayIcon.DoubleClick: self.showNormal(); self.raise_(); self.activateWindow()
    def _log(self,text): self._last_action=text; self.lbl_recent.setText(f"최근 실행: {text}")

    def toggle_keepalive(self):
        turn_on=not self.keepalive_running
        self.cfg["selected_key"]=normalize_key(self.combo_key.currentText()); self.cfg["cycle_min"]=int(self.spin_cycle.value())
        if turn_on:
            key=self.cfg["selected_key"]; ms=max(1,int(self.cfg["cycle_min"]))*60000
            self.keepalive_timer.stop()
            if key!="none":
                self.keepalive_timer.start(ms); self.keepalive_running=True; self.lbl_status.setText(pill("Keepalive On",True)); self._log(f"Keepalive 시작 ({key}, {self.cfg['cycle_min']}분)")
                self.btn_toggle.setText("Keepalive Stop"); self._do_keepalive()
            else: self._log("Keepalive 키가 'none'입니다.")
        else:
            self.keepalive_timer.stop(); self.keepalive_running=False; self.lbl_status.setText(pill("Keepalive Off",False)); self._log("Keepalive 중지"); self.btn_toggle.setText("Keepalive Start")

    def _do_keepalive(self):
        key=normalize_key(self.combo_key.currentText())
        if key=="none": self._log("주기 키: 사용 안함"); return
        try: pyauto_press_combo([key]); pyauto_press_combo([key]); self._log(f"주기 키 전송: {key}")
        except Exception as e: self._log(f"주기 키 실패: {e}")

    def _poll_mouse(self):
        pos=pyautogui.position(); self.lbl_mouse.setText(f"마우스: {pos.x}, {pos.y}")
        if self._cooldown: return
        use1,use2=self.chk_mon1.isChecked(), self.chk_mon2.isChecked()
        try: tol=max(0,int(self.tol_edit.text()))
        except Exception: tol=0
        curx,cury=pos.x,pos.y
        checks={0:[],1:[],2:[],3:[]}
        if use1:
            for idx in range(4):
                ax,ay=self.cfg["calibration"][0][idx]
                try: checks[idx].append((0,int(ax),int(ay)))
                except Exception: pass
        if use2:
            for idx in range(4):
                ax,ay=self.cfg["calibration"][1][idx]
                try: checks[idx].append((1,int(ax),int(ay)))
                except Exception: pass
        def match(ax,ay): 
            if tol<=0: return (curx==ax and cury==ay)
            return abs(curx-ax)<=tol and abs(cury-ay)<=tol
        hit_idx=None; hit_pos=None
        for corner_idx,entries in checks.items():
            for mon,ax,ay in entries:
                if match(ax,ay): hit_idx=corner_idx; hit_pos=(ax,ay); break
            if hit_idx is not None: break
        if self._inside_idx is None:
            if hit_idx is not None:
                self._inside_idx=hit_idx; self._inside_visual=hit_pos
                if hit_pos is not None: self._maybe_effect(hit_pos[0], hit_pos[1], hold=True)
        else:
            if hit_idx==self._inside_idx:
                pass
            else:
                fire_idx=self._inside_idx; vis=self._inside_visual; self._inside_idx=None; self._inside_visual=None
                try: self.overlay.hide_effect()
                except Exception: pass
                req_on=self.req_enables[fire_idx].isChecked(); req_key=normalize_key(self.req_combos[fire_idx].currentText())
                if req_on and req_key!="none":
                    if not is_key_down_simple(req_key):
                        self._log(f"코너 {fire_idx}: 조건 키({req_key.upper()})가 눌려있지 않아 실행 취소"); return
                if vis is not None: self._trigger_corner(fire_idx, visual_x=vis[0], visual_y=vis[1])
                else: self._trigger_corner(fire_idx)
                self._cooldown=True; cooldown=int(self.spin_cooldown.value()); QTimer.singleShot(max(0,cooldown), lambda: setattr(self,"_cooldown",False)); return

    def _launch_app(self,path):
        try:
            if not path: raise RuntimeError("경로 없음")
            if platform.system()=="Windows": os.startfile(path)  # type: ignore
            else: subprocess.Popen([path])
            return True,None
        except Exception as e: return False,str(e)

    def _maybe_effect(self,x,y,hold=False):
        if not self.chk_effect.isChecked(): return
        self.overlay.configure(
            effect_type=self.combo_effect.currentText(),
            max_radius=int(self.spin_effect_size.value()),
            duration_ms=int(self.spin_effect_dur.value()),
            color=getattr(self,"_effect_color",QColor("#5A82FF")),
            stroke_px=int(self.spin_effect_stroke.value()),
            stroke_opacity_percent=int(self.spin_effect_stroke_op.value()),
            fill_opacity_percent=int(self.spin_effect_fill_op.value())
        )
        self.overlay.show_effect(int(x), int(y), hold=hold)

    def _trigger_corner(self,idx, visual_x=None, visual_y=None):
        if self.app_enables[idx].isChecked():
            path=self.app_edits[idx].text().strip() or self.cfg["apps_paths"][idx]
            ok,err=self._launch_app(path)
            if ok: self._log(f"코너 {idx} 앱 실행: {os.path.basename(path) or path}")
            else: self._log(f"코너 {idx} 앱 실행 실패: {err}")
            return
        if self.hotkey_enables[idx].isChecked():
            keys=[normalize_key(k) for k in self.cfg["hotkeys"][idx] if normalize_key(k)!="none"]
            if not keys: self._log(f"코너 {idx} 단축키 없음"); return
            try: pyauto_press_combo(keys); self._log(f"코너 {idx} 실행: {'+'.join(k.upper() for k in keys)}")
            except Exception as e: self._log(f"코너 {idx} 실패: {e}"); return
            return
        self._log(f"코너 {idx}: 동작 비활성화")

    def _on_hotkey_assign(self):
        sender=self.sender(); _,r,c=sender.objectName().split("_"); r=int(r); c=int(c)
        keys_list=KeyCaptureDialog.capture(self); keys=[k for k in keys_list if k!="none"]
        while len(keys)<3: keys.append("none"); keys=keys[:3]
        self.cfg["hotkeys"][r]=keys
        for j,btn in enumerate(self.hotkey_btns[r]): btn.setText(self.cfg["hotkeys"][r][j].upper())
        self._log(f"코너 {r} 설정: {'+'.join([k.upper() for k in keys if k!='none']) or 'NONE'}")

    def _start_calibration(self):
        sender=self.sender(); _,mon,corner=sender.objectName().split("_"); mon=int(mon); corner=int(corner)
        pos=CalibrationDialog.capture(self)
        if pos is None: return
        x,y=pos; self.cfg["calibration"][mon][corner]=[x,y]
        cname=["LT","RT","LB","RB"][corner]; sender.setText(f"M{mon+1}-{cname}: {x}.{y}"); self._log(f"보정: M{mon+1}-{cname} = {x},{y}")

    def _save_clicked(self):
        self.cfg["use_monitor"][0]=self.chk_mon1.isChecked(); self.cfg["use_monitor"][1]=self.chk_mon2.isChecked()
        try: self.cfg["tolerance_px"]=max(0,int(self.tol_edit.text()))
        except Exception: self.cfg["tolerance_px"]=0
        self.cfg["selected_key"]=normalize_key(self.combo_key.currentText()); self.cfg["cycle_min"]=int(self.spin_cycle.value())
        self.cfg["autorun"]=self.chk_autorun.isChecked(); self.cfg["autostart_keepalive"]=self.chk_autostart_keepalive.isChecked(); self.cfg["autominimize_tray"]=self.chk_autominimize.isChecked()
        self.cfg["window_size"]=[int(self.spin_win_w.value()), int(self.spin_win_h.value())]; self.cfg["cooldown_ms"]=int(self.spin_cooldown.value())
        self.cfg["effect_enabled"]=self.chk_effect.isChecked(); self.cfg["effect_type"]=self.combo_effect.currentText()
        self.cfg["effect_size_px"]=int(self.spin_effect_size.value()); self.cfg["effect_duration_ms"]=int(self.spin_effect_dur.value())
        self.cfg["effect_color"]=getattr(self,"_effect_color",QColor("#5A82FF")).name()
        self.cfg["effect_stroke_px"]=int(self.spin_effect_stroke.value()); self.cfg["effect_stroke_opacity"]=int(self.spin_effect_stroke_op.value()); self.cfg["effect_fill_opacity"]=int(self.spin_effect_fill_op.value())
        for r in range(4):
            self.cfg["hotkeys_enabled"][r]=self.hotkey_enables[r].isChecked()
            self.cfg["apps_enabled"][r]=self.app_enables[r].isChecked()
            self.cfg["apps_paths"][r]=self.app_edits[r].text().strip()
            self.cfg["require_key_enabled"][r]=self.req_enables[r].isChecked()
            self.cfg["require_key_name"][r]=normalize_key(self.req_combos[r].currentText())
        if self.cfg["autorun"]:
            ok,err=set_windows_autorun(True)
            if not ok and err: QMessageBox.warning(self,"자동 실행 오류",f"자동 실행 설정 실패:\n{err}")
        else: set_windows_autorun(False)
        save_config(self.cfg)
        try: w,h=self.cfg["window_size"]; self.resize(int(w),int(h))
        except Exception: pass
        QMessageBox.information(self,"저장됨","설정이 저장되었습니다.")
    def _export_cfg(self):
        path,_=QFileDialog.getSaveFileName(self,"설정 내보내기",str(Path.home()/ "AutoHotCorner.json"),"JSON (*.json)")
        if not path: return
        try: Path(path).write_text(json.dumps(self.cfg, ensure_ascii=False, indent=2), encoding="utf-8"); QMessageBox.information(self,"완료","설정을 내보냈습니다.")
        except Exception as e: QMessageBox.warning(self,"오류",f"내보내기 실패: {e}")
    def _import_cfg(self):
        path,_=QFileDialog.getOpenFileName(self,"설정 가져오기",str(Path.home()),"JSON (*.json)")
        if not path: return
        try:
            cfg=json.loads(Path(path).read_text(encoding="utf-8")); base=default_config(); base.update(cfg); self.cfg=base
            self.combo_key.setCurrentText(self.cfg.get("selected_key","f15")); self.spin_cycle.setValue(int(self.cfg.get("cycle_min",1)))
            self.chk_mon1.setChecked(bool(self.cfg["use_monitor"][0])); self.chk_mon2.setChecked(bool(self.cfg["use_monitor"][1])); self.tol_edit.setText(str(self.cfg.get("tolerance_px",0)))
            self.chk_autorun.setChecked(bool(self.cfg.get("autorun",False) or get_windows_autorun())); self.chk_autostart_keepalive.setChecked(bool(self.cfg.get("autostart_keepalive",False))); self.chk_autominimize.setChecked(bool(self.cfg.get("autominimize_tray",False)))
            ws=self.cfg.get("window_size",[620,720]); self.spin_win_w.setValue(int(ws[0])); self.spin_win_h.setValue(int(ws[1])); self.resize(int(ws[0]),int(ws[1]))
            self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms",500)))
            self.chk_effect.setChecked(bool(self.cfg.get("effect_enabled",True))); self.combo_effect.setCurrentText(self.cfg.get("effect_type","Ripple"))
            self.spin_effect_size.setValue(int(self.cfg.get("effect_size_px",120))); self.spin_effect_dur.setValue(int(self.cfg.get("effect_duration_ms",450)))
            self._effect_color=QColor(self.cfg.get("effect_color","#5A82FF")); self._update_color_preview()
            self.spin_effect_stroke.setValue(int(self.cfg.get("effect_stroke_px",4))); self.spin_effect_stroke_op.setValue(int(self.cfg.get("effect_stroke_opacity",60))); self.spin_effect_fill_op.setValue(int(self.cfg.get("effect_fill_opacity",15)))
            for r in range(4):
                for c in range(3): self.hotkey_btns[r][c].setText(self.cfg["hotkeys"][r][c].upper())
                self.hotkey_enables[r].setChecked(bool(self.cfg["hotkeys_enabled"][r]))
                self.app_enables[r].setChecked(bool(self.cfg["apps_enabled"][r]))
                self.app_edits[r].setText(self.cfg["apps_paths"][r]); self.app_name_labels[r].setText(os.path.basename(self.cfg["apps_paths"][r]) or "(미선택)")
                self.req_enables[r].setChecked(bool(self.cfg["require_key_enabled"][r])); self.req_combos[r].setCurrentText(self.cfg["require_key_name"][r])
            QMessageBox.information(self,"완료","설정을 가져왔습니다.")
        except Exception as e: QMessageBox.warning(self,"오류",f"가져오기 실패: {e}")
    def _reset_cfg(self):
        self.cfg=default_config(); save_config(self.cfg)
        self.combo_key.setCurrentText(self.cfg["selected_key"]); self.spin_cycle.setValue(self.cfg["cycle_min"])
        self.chk_mon1.setChecked(False); self.chk_mon2.setChecked(False); self.tol_edit.setText("0")
        self.chk_autorun.setChecked(False); self.chk_autostart_keepalive.setChecked(False); self.chk_autominimize_tray=False
        ws=self.cfg.get("window_size",[620,720]); self.spin_win_w.setValue(int(ws[0])); self.spin_win_h.setValue(int(ws[1])); self.resize(int(ws[0]),int(ws[1]))
        self.spin_cooldown.setValue(int(self.cfg.get("cooldown_ms",500)))
        self.chk_effect.setChecked(True); self.combo_effect.setCurrentText("Ripple"); self.spin_effect_size.setValue(120); self.spin_effect_dur.setValue(450)
        self._effect_color=QColor("#5A82FF"); self._update_color_preview(); self.spin_effect_stroke.setValue(4); self.spin_effect_stroke_op.setValue(60); self.spin_effect_fill_op.setValue(15)
        for r in range(4):
            for c in range(3): self.hotkey_btns[r][c].setText("NONE")
            self.hotkey_enables[r].setChecked(False); self.app_enables[r].setChecked(False)
            self.app_edits[r].setText(""); self.app_name_labels[r].setText("(미선택)")
            self.req_enables[r].setChecked(False); self.req_combos[r].setCurrentText("none")
        QMessageBox.information(self,"초기화","설정을 초기화했습니다.")
    def changeEvent(self,event):
        if event.type()==event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized: self.hide()
    def closeEvent(self,event):
        self.keepalive_timer.stop(); self.corner_timer.stop(); self.tray.hide(); save_config(self.cfg); event.accept()

def main():
    app=QApplication(sys.argv)
    apply_dark_theme(app)
    w=MainWindow()
    icon_path=resource_path(ICON_NAME)
    if os.path.exists(icon_path): app.setWindowIcon(QIcon(icon_path))
    w.setWindowIcon(QIcon(icon_path)) if os.path.exists(icon_path) else None
    w.setWindowTitle(f"{APP_NAME} v{VERSION}")
    w.setStyleSheet(CARD_QSS)
    w.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
