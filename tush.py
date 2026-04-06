import sys, time, threading, ctypes, keyboard, mouse, webbrowser, json, psutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# =========================
# ACTUALIZACIÓN SEGURA
# =========================
import os
import subprocess

def check_update():
    if not os.path.exists("version.json"):
        return
    try:
        with open("version.json", "r") as f:
            data = json.load(f)
        local = data.get("current_version", "")
        latest = data.get("latest_version", "")
        if local != latest and os.path.exists("update.py"):
            subprocess.Popen([sys.executable, "update.py"])
    except Exception as e:
        print("Error al comprobar update:", e)

# Llamamos al inicio
check_update()

# =========================
# WINDOWS API
# =========================
user32 = ctypes.WinDLL('user32', use_last_error=True)
def get_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value
def is_roblox():
    try: return "Roblox" in get_window_title()
    except: return False

# =========================
# SUBIR PRIORIDAD DE ROBLOX
# =========================
def set_roblox_high_priority():
    for proc in psutil.process_iter(['name', 'pid']):
        if "RobloxPlayerBeta.exe" in proc.info['name']:
            try:
                p = psutil.Process(proc.info['pid'])
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            except: pass

threading.Thread(target=lambda: [set_roblox_high_priority() or time.sleep(5) for _ in iter(int,1)], daemon=True).start()

# =========================
# MACRO OPTIMIZADO CON KPS REAL
# =========================
class Macro:
    def __init__(self):
        self.action_key = "f"
        self.toggle_key = "f8"
        self.kps = 30
        self.active = False
        self.mode_toggle = True
        threading.Thread(target=self.loop, daemon=True).start()

    def set_kps(self, kps):
        try: self.kps = max(1, int(kps))
        except: pass

    def set_action_key(self, key): self.action_key = key
    def set_toggle_key(self, key): self.toggle_key = key
    def set_mode(self, toggle: bool): self.mode_toggle = toggle

    def press(self):
        try:
            if self.action_key.startswith("mouse_"):
                mouse.click(self.action_key.split("_")[1])
            else:
                keyboard.press_and_release(self.action_key)
        except: pass

    def loop(self):
        next_click = time.perf_counter()
        while True:
            if self.active and is_roblox():
                now = time.perf_counter()
                if now >= next_click:
                    self.press()
                    next_click = now + 1/self.kps
                else:
                    time.sleep(max(0.0005, next_click - now))
            else:
                time.sleep(0.01)
                next_click = time.perf_counter()

# =========================
# TOGGLE LISTENER
# =========================
class ToggleListener(threading.Thread):
    def __init__(self, macro):
        super().__init__(daemon=True)
        self.macro = macro
        self.last_state = False
        self.last_toggle_time = 0
    def run(self):
        while True:
            try:
                key = self.macro.toggle_key
                pressed = keyboard.is_pressed(key) if not key.startswith("mouse_") else mouse.is_pressed(button=key.split("_")[1])
                now = time.perf_counter()
                if self.macro.mode_toggle:
                    if pressed and not self.last_state and now - self.last_toggle_time >= 0.2:
                        self.macro.active = not self.macro.active
                        self.last_toggle_time = now
                    self.last_state = pressed
                else:
                    self.macro.active = pressed
            except: pass
            time.sleep(0.01)

# =========================
# UI NEGRA MINIMALISTA
# =========================
class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.version = "v1.7"
        self.macro = Macro()
        self.listener = ToggleListener(self.macro)
        self.listener.start()
        self.listening = False
        self.drag_pos = None
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Tush Clash Macro")
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)

        # Titulo
        title = QLabel(f"Tush Clash Macro - {self.version}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px;font-weight:bold;color:white;")
        layout.addWidget(title)

        # KPS
        layout.addWidget(QLabel("KPS"))
        self.kps_input = QLineEdit(str(self.macro.kps))
        self.kps_input.setStyleSheet(self.input_style())
        self.kps_input.setFixedHeight(40)
        self.kps_input.textChanged.connect(lambda t: self.macro.set_kps(t))
        layout.addWidget(self.kps_input)

        # Action Key
        layout.addWidget(QLabel("Action Key"))
        self.action = QComboBox()
        self.action.addItems(["f","e","space","q","r","t"])
        self.action.setFixedHeight(40)
        self.action.setStyleSheet(self.input_style())
        self.action.currentTextChanged.connect(self.macro.set_action_key)
        layout.addWidget(self.action)

        # Hotkey
        hotkey_layout = QHBoxLayout()
        self.hotkey_btn = QPushButton("SET HOTKEY")
        self.hotkey_btn.setFixedHeight(40)
        self.hotkey_btn.setStyleSheet(self.btn_style())
        self.hotkey_btn.clicked.connect(self.set_hotkey)
        hotkey_layout.addWidget(self.hotkey_btn)

        self.mode_checkbox = QCheckBox("Toggle Mode")
        self.mode_checkbox.setChecked(True)
        self.mode_checkbox.setStyleSheet("color:white;font-size:16px;")
        self.mode_checkbox.stateChanged.connect(lambda s: self.macro.set_mode(self.mode_checkbox.isChecked()))
        hotkey_layout.addWidget(self.mode_checkbox)
        layout.addLayout(hotkey_layout)

        # Boton creador
        creator_btn = QPushButton("CREADOR")
        creator_btn.setFixedHeight(40)
        creator_btn.setStyleSheet(self.btn_style())
        creator_btn.clicked.connect(lambda: webbrowser.open("https://guns.lol/2by"))
        layout.addWidget(creator_btn)

        layout.addStretch()

    def input_style(self):
        return "padding:10px;border-radius:10px;background:#1e1e1e;color:white;font-size:16px;border:2px solid rgba(255,255,255,0.3);"
    def btn_style(self):
        return "padding:10px;border-radius:10px;background:#1e1e1e;color:white;font-size:16px;border:2px solid rgba(255,255,255,0.3);"

    # DRAG
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton: self.drag_pos=event.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if self.drag_pos and event.buttons()==Qt.LeftButton: self.move(event.globalPos()-self.drag_pos)
    def mouseReleaseEvent(self,event): self.drag_pos=None

    # HOTKEY
    def set_hotkey(self):
        if self.listening: return
        self.listening=True
        self.hotkey_btn.setText("PRESS KEY...")
        def detect():
            while self.listening:
                for btn in ["left","right","middle","x","x2"]:
                    if mouse.is_pressed(button=btn): self.apply_hotkey(f"mouse_{btn}"); return
                e=keyboard.read_event(suppress=False)
                if e.event_type==keyboard.KEY_DOWN: self.apply_hotkey(e.name); return
        threading.Thread(target=detect,daemon=True).start()
    def apply_hotkey(self,key):
        self.macro.set_toggle_key(key)
        self.hotkey_btn.setText(key.upper())
        self.listening=False

    # FONDO NEGRO
    def paintEvent(self,event):
        p=QPainter(self)
        p.fillRect(self.rect(), QColor("#000000"))

# =========================
# RUN
# =========================
if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
