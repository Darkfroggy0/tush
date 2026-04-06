import sys, time, threading, ctypes, keyboard, mouse, requests, os, webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
# AUTO UPDATE
# =========================
def check_update():
    url_version = "https://raw.githubusercontent.com/usuario/repositorio/main/version.txt"
    url_script = "https://raw.githubusercontent.com/usuario/repositorio/main/tush.py"
    current_version = "1.7"
    try:
        r = requests.get(url_version, timeout=5)
        if r.status_code != 200: return
        latest_version = r.text.strip()
        if latest_version != current_version:
            reply = QMessageBox.question(None, "Update", f"Nueva versión {latest_version} disponible. ¿Actualizar?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                r2 = requests.get(url_script, timeout=10)
                if r2.status_code == 200:
                    with open(sys.argv[0], "wb") as f: f.write(r2.content)
                    QMessageBox.information(None, "Update", "Actualización completada. Reiniciando...")
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else: QMessageBox.warning(None, "Update", "Error al descargar script.")
    except: pass

# =========================
# MACRO
# =========================
class Macro:
    def __init__(self):
        self.action_key = "f"
        self.toggle_key = "f8"
        self.kps = 30
        self.active = False
        self.mode_toggle = True
        self.lock = threading.Lock()
        threading.Thread(target=self.loop, daemon=True).start()
    def set_kps(self, kps):
        try: self.kps = max(1, min(2000, int(kps)))
        except: pass
    def set_action_key(self, key): self.action_key = key
    def set_toggle_key(self, key): self.toggle_key = key
    def set_mode(self, toggle: bool): self.mode_toggle = toggle
    def press(self):
        try:
            if self.action_key.startswith("mouse_"): mouse.click(self.action_key.split("_")[1])
            else: keyboard.press_and_release(self.action_key)
        except: pass
    def loop(self):
        next_click = time.perf_counter()
        while True:
            if not self.active or not is_roblox():
                time.sleep(0.005)
                next_click = time.perf_counter()
                continue
            now = time.perf_counter()
            if now >= next_click:
                self.press()
                next_click = now + 1/self.kps
            else:
                time.sleep(max(0.0005, next_click - now))

# =========================
# TOGGLE LISTENER
# =========================
class ToggleListener(threading.Thread):
    def __init__(self, macro):
        super().__init__(daemon=True)
        self.macro = macro
        self.last_state = False
        self.last_toggle_time = 0
        self.cooldown = 0.2
    def run(self):
        while True:
            try:
                key = self.macro.toggle_key
                pressed = False
                if key.startswith("mouse_"): pressed = mouse.is_pressed(button=key.split("_")[1])
                else: pressed = keyboard.is_pressed(key)
                now = time.perf_counter()
                if self.macro.mode_toggle:
                    if pressed and not self.last_state and now - self.last_toggle_time >= self.cooldown:
                        self.macro.active = not self.macro.active
                        self.last_toggle_time = now
                    self.last_state = pressed
                else: self.macro.active = pressed
            except: pass
            time.sleep(0.005)

# =========================
# UI
# =========================
class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.version = "v1.6"
        self.macro = Macro()
        self.listener = ToggleListener(self.macro)
        self.listener.start()
        self.listening = False
        self.drag_pos = None
        self.gradient_offset = 0
        self.init_ui()
        self.start_animation()

    def init_ui(self):
        self.setFixedSize(500, 450)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Tush Clash Macro")
        self.setWindowIcon(QIcon("icon.png"))  # Coloca tu icono .png

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,25,25,25)
        layout.setSpacing(15)

        # Título
        title = QLabel("Tush Clash Macro")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:28px;font-weight:bold;color:#d4af37;")
        layout.addWidget(title)

        # KPS
        layout.addWidget(QLabel("KPS"))
        self.kps_input = QLineEdit("30")
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
        layout.addWidget(QLabel("Hotkey"))
        hotkey_layout = QHBoxLayout()
        self.hotkey_btn = QPushButton("SET HOTKEY")
        self.hotkey_btn.setFixedHeight(40)
        self.hotkey_btn.setStyleSheet(self.btn_style())
        self.hotkey_btn.clicked.connect(self.set_hotkey)
        hotkey_layout.addWidget(self.hotkey_btn)

        self.mode_checkbox = QCheckBox("Toggle Mode")
        self.mode_checkbox.setChecked(True)
        self.mode_checkbox.setStyleSheet("color:#d4af37;font-size:16px;")
        self.mode_checkbox.stateChanged.connect(lambda s: self.macro.set_mode(self.mode_checkbox.isChecked()))
        hotkey_layout.addWidget(self.mode_checkbox)
        layout.addLayout(hotkey_layout)

        # Botón Creador
        creator_btn = QPushButton("CREADOR")
        creator_btn.setFixedHeight(40)
        creator_btn.setStyleSheet(self.btn_style())
        creator_btn.clicked.connect(lambda: webbrowser.open("https://guns.lol/2by"))
        layout.addWidget(creator_btn)

        layout.addStretch()

    def input_style(self):
        return "padding:10px;border-radius:12px;background:#1e1e1e;color:#d4af37;font-size:18px;border:2px solid rgba(212,175,55,128);"
    def btn_style(self):
        return "padding:10px;border-radius:12px;background:#1e1e1e;color:#d4af37;font-size:16px;border:2px solid rgba(212,175,55,128);"

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

    # BACKGROUND ANIMADO
    def start_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)
    def paintEvent(self,event):
        p=QPainter(self)
        gradient=QLinearGradient(0,0,self.width(),self.height())
        gradient.setColorAt(0, QColor.fromHsv((self.gradient_offset)%360,180,50))
        gradient.setColorAt(1, QColor.fromHsv((self.gradient_offset+60)%360,180,100))
        self.gradient_offset+=1
        p.fillRect(self.rect(), gradient)

# =========================
# RUN
# =========================
if __name__=="__main__":
    app=QApplication(sys.argv)
    check_update()  # Verifica actualizaciones antes de abrir UI
    ui=UI()
    ui.show()
    sys.exit(app.exec_())
