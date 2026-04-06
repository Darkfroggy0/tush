import sys
import time
import threading
import ctypes
import keyboard
import mouse
import webbrowser
import json
import requests
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# =========================
# 🪟 WINDOWS API
# =========================
user32 = ctypes.WinDLL('user32', use_last_error=True)

def get_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def is_roblox():
    try:
        return "Roblox" in get_window_title()
    except:
        return False

# =========================
# ⚡ MACRO ENGINE
# =========================
class Macro:
    def __init__(self):
        self.action_key = "f"
        self.toggle_key = "f8"
        self.kps = 30
        self.active = False
        self.lock = threading.Lock()
        threading.Thread(target=self.loop, daemon=True).start()

    def set_kps(self, kps):
        self.kps = max(1, min(2000, kps))

    def set_action_key(self, key):
        self.action_key = key

    def set_toggle_key(self, key):
        self.toggle_key = key

    def press(self):
        try:
            if self.action_key.startswith("mouse_"):
                mouse.click(self.action_key.split("_")[1])
            else:
                keyboard.press_and_release(self.action_key)
        except:
            pass

    def loop(self):
        while True:
            try:
                if not self.active or not is_roblox():
                    time.sleep(0.002)
                    continue

                with self.lock:
                    interval = 1 / self.kps
                    start = time.perf_counter()
                    self.press()
                    elapsed = time.perf_counter() - start
                    remaining = interval - elapsed
                    if remaining > 0:
                        step = 0.001
                        while remaining > 0:
                            if not self.active:
                                break
                            time.sleep(min(step, remaining))
                            remaining -= step
            except:
                time.sleep(0.01)

# =========================
# 🎮 TOGGLE LISTENER (CON COOLDOWN)
# =========================
class ToggleListener(threading.Thread):
    def __init__(self, macro):
        super().__init__(daemon=True)
        self.macro = macro
        self.last_state = False
        self.last_toggle_time = 0
        self.cooldown = 0.2  # segundos

    def run(self):
        while True:
            try:
                key = self.macro.toggle_key
                pressed = False
                if key.startswith("mouse_"):
                    pressed = mouse.is_pressed(button=key.split("_")[1])
                else:
                    pressed = keyboard.is_pressed(key)

                current_time = time.perf_counter()
                if pressed and not self.last_state:
                    # Verifica cooldown
                    if current_time - self.last_toggle_time >= self.cooldown:
                        self.macro.active = not self.macro.active
                        self.last_toggle_time = current_time
                    self.last_state = True
                elif not pressed:
                    self.last_state = False
            except:
                pass
            time.sleep(0.01)
# =========================
# 🌐 AUTO UPDATE (SEGURO)
# =========================
def check_update():
    url_version = "https://raw.githubusercontent.com/usuario/repositorio/main/version.txt"
    url_script = "https://raw.githubusercontent.com/usuario/repositorio/main/tush.py"
    current_version = "1.5"
    try:
        r = requests.get(url_version, timeout=5)
        if r.status_code != 200:
            print("[UPDATE] No se pudo verificar la versión")
            return
        latest_version = r.text.strip()
        if latest_version != current_version:
            print(f"[UPDATE] Nueva versión {latest_version} encontrada. Actualizando...")
            r2 = requests.get(url_script, timeout=10)
            if r2.status_code == 200:
                with open(sys.argv[0], "wb") as f:
                    f.write(r2.content)
                print("[UPDATE] Actualización completada. Reiniciando...")
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                print(f"[UPDATE] Error al descargar script: {r2.status_code}")
    except Exception as e:
        print(f"[UPDATE] Error de actualización: {e}")

# =========================
# 🎨 UI (RE-DISEÑADA)
# =========================
class UI(QWidget):
    def __init__(self):
        super().__init__()
        threading.Thread(target=check_update, daemon=True).start()
        self.macro = Macro()
        self.listener = ToggleListener(self.macro)
        self.listener.start()
        self.listening = False
        self.drag_pos = None
        self.version = "v1.5"
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(420, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
        QWidget {
            background: #121212;
            color: white;
            border-radius: 15px;
            font-family: Arial, sans-serif;
        }
        QLineEdit, QComboBox, QPushButton {
            padding: 12px;
            border-radius: 10px;
            background: #1e1e1e;
            font-size: 14px;
        }
        QPushButton:hover { background: #2a2a2a; }
        QLabel { font-size: 14px; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        title = QLabel("Tush Clash")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(title)

        # KPS
        main_layout.addWidget(QLabel("KPS"))
        self.kps = QLineEdit("30")
        self.kps.setAlignment(Qt.AlignCenter)
        self.kps.textChanged.connect(self.update_kps)
        main_layout.addWidget(self.kps)

        # Acción
        main_layout.addWidget(QLabel("Action Key"))
        self.action = QComboBox()
        self.action.addItems(["f","e","space","mouse_left","mouse_right","mouse_middle","mouse_x","mouse_x2"])
        self.action.currentTextChanged.connect(self.macro.set_action_key)
        main_layout.addWidget(self.action)

        # Toggle Key
        main_layout.addWidget(QLabel("Toggle Key"))
        self.hotkey = QPushButton("SET TOGGLE KEY")
        self.hotkey.clicked.connect(self.set_hotkey)
        main_layout.addWidget(self.hotkey)

        # Config buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(self.load_config)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        main_layout.addLayout(btn_layout)

        # Creator
        creator = QPushButton("CREADOR")
        creator.clicked.connect(lambda: webbrowser.open("https://guns.lol/2by"))
        main_layout.addWidget(creator)

        main_layout.addStretch()
        version_label = QLabel(self.version)
        version_label.setAlignment(Qt.AlignRight)
        version_label.setStyleSheet("color: #888888; font-size: 11px;")
        main_layout.addWidget(version_label)

    # =========================
    # 🖱️ DRAG WINDOW
    # =========================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    # =========================
    # 🎯 SET TOGGLE KEY
    # =========================
    def set_hotkey(self):
        if self.listening:
            return
        self.listening = True
        self.hotkey.setText("PRESS KEY...")
        def detect():
            while self.listening:
                for btn in ["left","right","middle","x","x2"]:
                    if mouse.is_pressed(button=btn):
                        self.apply_hotkey(f"mouse_{btn}")
                        return
                event = keyboard.read_event(suppress=False)
                if event.event_type == keyboard.KEY_DOWN:
                    self.apply_hotkey(event.name)
                    return
        threading.Thread(target=detect, daemon=True).start()

    def apply_hotkey(self, key):
        self.macro.set_toggle_key(key)
        self.hotkey.setText(key.upper())
        self.listening = False

    # =========================
    # 💾 CONFIG
    # =========================
    def save_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if not path:
            return
        data = {
            "kps": self.kps.text(),
            "action": self.action.currentText(),
            "toggle": self.macro.toggle_key
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def load_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if not path:
            return
        with open(path) as f:
            data = json.load(f)
        self.kps.setText(str(data.get("kps", 30)))
        self.action.setCurrentText(data.get("action", "f"))
        toggle = data.get("toggle", "f8")
        self.macro.set_toggle_key(toggle)
        self.hotkey.setText(toggle.upper())

    def update_kps(self):
        try:
            self.macro.set_kps(int(self.kps.text()))
        except:
            pass

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = UI()
    ui.setWindowOpacity(0)
    ui.show()
    anim = QPropertyAnimation(ui, b"windowOpacity")
    anim.setDuration(600)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.setEasingCurve(QEasingCurve.InOutQuad)
    anim.start()
    sys.exit(app.exec_())
