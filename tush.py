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
        self.hold_key = "f8"
        self.kps = 30
        self.active = False
        self.lock = threading.Lock()
        threading.Thread(target=self.loop, daemon=True).start()

    def set_kps(self, kps):
        self.kps = max(1, min(2000, kps))

    def set_action_key(self, key):
        self.action_key = key

    def set_hold_key(self, key):
        self.hold_key = key

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
# 🎮 INPUT LISTENER
# =========================
class InputListener(threading.Thread):
    def __init__(self, macro):
        super().__init__(daemon=True)
        self.macro = macro

    def run(self):
        while True:
            try:
                key = self.macro.hold_key
                if key.startswith("mouse_"):
                    self.macro.active = mouse.is_pressed(button=key.split("_")[1])
                else:
                    self.macro.active = keyboard.is_pressed(key)
            except:
                self.macro.active = False

            time.sleep(0.001)

# =========================
# 🌐 AUTO UPDATE
# =========================
def check_update():
    url_version = "https://raw.githubusercontent.com/usuario/repositorio/main/version.txt"
    url_script = "https://raw.githubusercontent.com/usuario/repositorio/main/tush.py"
    current_version = "1.0"
    try:
        r = requests.get(url_version, timeout=5)
        latest_version = r.text.strip()
        if latest_version != current_version:
            r2 = requests.get(url_script)
            with open(sys.argv[0], "wb") as f:
                f.write(r2.content)
            # reinicia la app con la versión nueva
            os.execl(sys.executable, sys.executable, *sys.argv)
    except:
        pass

# =========================
# 🎨 UI (DRAGGABLE)
# =========================
class UI(QWidget):
    def __init__(self):
        super().__init__()

        # revisar updates
        threading.Thread(target=check_update, daemon=True).start()

        self.macro = Macro()
        self.listener = InputListener(self.macro)
        self.listener.start()

        self.listening = False
        self.drag_pos = None

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(420, 460)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)

        title = QLabel("Tush Clash")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")

        self.kps = QLineEdit("30")
        self.kps.setAlignment(Qt.AlignCenter)
        self.kps.textChanged.connect(self.update_kps)

        self.action = QComboBox()
        self.action.addItems([
            "f","e","space",
            "mouse_left","mouse_right",
            "mouse_middle","mouse_x","mouse_x2"
        ])
        self.action.currentTextChanged.connect(self.macro.set_action_key)

        self.hotkey = QPushButton("SET HOLD KEY")
        self.hotkey.clicked.connect(self.set_hotkey)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)

        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(self.load_config)

        creator = QPushButton("CREADOR")
        creator.clicked.connect(lambda: webbrowser.open("https://guns.lol/2by"))

        layout.addWidget(title)
        layout.addWidget(QLabel("KPS"))
        layout.addWidget(self.kps)
        layout.addWidget(QLabel("Action"))
        layout.addWidget(self.action)
        layout.addWidget(QLabel("Hold Key"))
        layout.addWidget(self.hotkey)
        layout.addWidget(save_btn)
        layout.addWidget(load_btn)
        layout.addStretch()
        layout.addWidget(creator)

        self.setStyleSheet("""
        QWidget {
            background: #121212;
            color: white;
            border-radius: 15px;
        }

        QLineEdit, QComboBox, QPushButton {
            padding: 10px;
            border-radius: 10px;
            background: #1e1e1e;
        }

        QPushButton:hover {
            background: #2a2a2a;
        }
        """)

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
    # 🎯 HOTKEY
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
        self.macro.set_hold_key(key)
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
            "hold": self.macro.hold_key
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

        hold = data.get("hold", "f8")
        self.macro.set_hold_key(hold)
        self.hotkey.setText(hold.upper())

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

    # Animación de apertura (fade-in)
    ui.setWindowOpacity(0)
    ui.show()

    anim = QPropertyAnimation(ui, b"windowOpacity")
    anim.setDuration(600)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.setEasingCurve(QEasingCurve.InOutQuad)
    anim.start()

    sys.exit(app.exec_())
