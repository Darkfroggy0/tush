import sys, time, threading, ctypes, keyboard, mouse, webbrowser, psutil, subprocess, uuid, platform, requests, os, hashlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# =========================
# CONFIGURACIÓN
# =========================
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1490952754674532483/VF5gThbKFvEKlPP2Mm5pec6iUuyFyl4XdlKFnFM7gTP6vpqzQa62dPBBhS42l4S4ShY_"

GITHUB_BAN_URL = "https://raw.githubusercontent.com/Darkfroggy0/tush/refs/heads/main/HWID%20Baneados"
GITHUB_LICENSE_URL = "https://raw.githubusercontent.com/Darkfroggy0/tush/refs/heads/main/Linc"
GITHUB_LATEST_URL = "https://raw.githubusercontent.com/Darkfroggy0/tush/refs/heads/main/tush.py"

CURRENT_VERSION = "v2.8"

# =========================
# GENERAR HWID
# =========================
def get_hwid():
    try:
        output = subprocess.check_output('wmic csproduct get uuid', shell=True, text=True, stderr=subprocess.DEVNULL)
        mb_uuid = output.strip().split('\n')[1].strip()
        try:
            mg = subprocess.check_output('reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid', 
                                        shell=True, text=True, stderr=subprocess.DEVNULL)
            machine_guid = mg.strip().split()[-1]
        except:
            machine_guid = "unknown"
        combined = f"{mb_uuid}-{machine_guid}-{platform.node()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined))
    except:
        return str(uuid.getnode())

HWID = get_hwid()

# =========================
# CARGAR BANEADOS
# =========================
def load_banned_hwids():
    try:
        r = requests.get(GITHUB_BAN_URL, timeout=8)
        r.raise_for_status()
        return {line.strip() for line in r.text.splitlines() if line.strip() and not line.startswith('#')}
    except:
        return set()

BANNED_HWIDS = load_banned_hwids()

if HWID in BANNED_HWIDS:
    QMessageBox.critical(None, "ACCESO DENEGADO", 
        "Has sido baneado.\n\n"
        "Si crees que es un error agrega al Creador de la macro:\n\n"
        ".2by_ en Discord\n\n"
        "O contáctalo por sus otras redes:\n"
        "https://guns.lol/2by")
    sys.exit(1)

# =========================
# ACTUALIZACIÓN AUTOMÁTICA AL INICIO (Sin preguntar)
# =========================
def auto_update():
    try:
        response = requests.get(GITHUB_LATEST_URL, timeout=12)
        response.raise_for_status()
        latest_code = response.text

        # Comparar versión actual con la del GitHub
        with open(__file__, "r", encoding="utf-8") as f:
            local_code = f.read()

        if hashlib.md5(local_code.encode('utf-8')).hexdigest() == hashlib.md5(latest_code.encode('utf-8')).hexdigest():
            return  # No hay actualización

        # Hay actualización → Proceder automáticamente
        updater_script = "tush_updater.bat"
        with open(updater_script, "w", encoding="utf-8") as f:
            f.write('@echo off\n')
            f.write('title Tush Macro - Actualizacion Automatica\n')
            f.write('echo ===============================================\n')
            f.write('echo          Actualizando Tush Macro...\n')
            f.write('echo ===============================================\n')
            f.write('echo.\n')
            f.write('echo Descargando nueva version...\n')
            f.write('timeout /t 2 >nul\n')
            f.write('echo Reemplazando archivos...\n')
            f.write('move /y "tush_new.py" "tush.py" >nul 2>&1\n')
            f.write('echo.\n')
            f.write('echo Actualizacion completada correctamente.\n')
            f.write('echo.\n')
            f.write('echo Presiona alguna tecla para cerrar el cmd y poder usar la macro...\n')
            f.write('pause >nul\n')
            f.write('start "" "TushMacro.exe"\n')
            f.write('del "%~f0"\n')
            f.write('exit\n')

        # Guardar la nueva versión
        with open("tush_new.py", "w", encoding="utf-8") as f:
            f.write(latest_code)

        # Ejecutar el actualizador en una ventana CMD visible
        subprocess.Popen(['cmd', '/c', updater_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        sys.exit(0)   # Cerrar el programa actual

    except Exception as e:
        print(f"Error en auto-update: {e}")  # Solo para debug

# =========================
# CARGAR LICENCIAS
# =========================
def load_licenses():
    try:
        r = requests.get(GITHUB_LICENSE_URL, timeout=8)
        r.raise_for_status()
        licenses = {}
        for line in r.text.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = [x.strip() for x in line.split('=', 1)]
                licenses[key] = value
        return licenses
    except:
        return {}

# =========================
# NOTIFICACIÓN DE LICENCIA
# =========================
def notify_license_request(license_key, hwid):
    notified_file = "notified_licenses.txt"
    entry = f"{license_key}|{hwid}"
    
    if os.path.exists(notified_file):
        with open(notified_file, "r", encoding="utf-8") as f:
            if entry in f.read():
                return

    try:
        data = {
            "username": "Tush License Bot",
            "content": "<@1140745091191939184>",
            "embeds": [{
                "title": "🔑 Nueva Solicitud de Licencia",
                "color": 0xffaa00,
                "fields": [
                    {"name": "Licencia", "value": f"`{license_key}`", "inline": False},
                    {"name": "HWID", "value": f"`{hwid}`", "inline": False},
                    {"name": "PC", "value": platform.node(), "inline": True},
                    {"name": "Usuario", "value": os.getlogin(), "inline": True},
                    {"name": "Hora", "value": time.strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
                ],
                "footer": {"text": "Agrega el HWID en el archivo Linc de GitHub"}
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=data, timeout=6)
        
        with open(notified_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except:
        pass

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))

    # === ACTUALIZACIÓN AUTOMÁTICA AL INICIO ===
    auto_update()

    # =========================
    # SISTEMA DE LICENCIA
    # =========================
    license_file = "license.key"

    if not os.path.exists(license_file):
        while True:
            license_key, ok = QInputDialog.getText(None, "Licencia Requerida", 
                "Ingresa tu licencia:")
            if not ok or not license_key.strip():
                sys.exit(0)

            license_key = license_key.strip()
            licenses = load_licenses()

            if license_key in licenses:
                registered_hwid = licenses[license_key]
                
                if registered_hwid == HWID:
                    with open(license_file, "w", encoding="utf-8") as f:
                        f.write(f"{license_key}\n{HWID}")
                    QMessageBox.information(None, "Éxito", "Licencia activada correctamente.")
                    break
                elif registered_hwid == "" or registered_hwid.lower() in ["", "libre", "pendiente", "free"]:
                    notify_license_request(license_key, HWID)
                    QMessageBox.information(None, "Licencia Libre", 
                        "Esta licencia está disponible.\nSe ha enviado una solicitud al creador.\n"
                        "Espera a que la vincule con tu HWID.")
                else:
                    QMessageBox.critical(None, "Error", "Esta licencia ya está vinculada a otro HWID.\nContacta con 2by.")
            else:
                QMessageBox.critical(None, "Error", "Esta licencia no existe en el sistema.")
    else:
        with open(license_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        if len(lines) < 2 or lines[1] != HWID:
            QMessageBox.critical(None, "Error", "Esta licencia no corresponde a este dispositivo.\nContacta con 2by.")
            if os.path.exists(license_file):
                os.remove(license_file)
            sys.exit(1)

    # =========================
    # WINDOWS API + MACRO + UI
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

    def set_roblox_high_priority():
        for proc in psutil.process_iter(['name', 'pid']):
            if "RobloxPlayerBeta.exe" in (proc.info.get('name') or ""):
                try:
                    psutil.Process(proc.info['pid']).nice(psutil.HIGH_PRIORITY_CLASS)
                except:
                    pass

    threading.Thread(target=lambda: [set_roblox_high_priority() or time.sleep(5) for _ in iter(int,1)], daemon=True).start()

    class Macro:
        def __init__(self):
            self.action_key = "f"
            self.toggle_key = "f8"
            self.kps = 30
            self.active = False
            self.mode_toggle = True
            self.is_holding = False
            threading.Thread(target=self.loop, daemon=True).start()

        def set_kps(self, kps):
            try: self.kps = max(1, int(kps))
            except: pass
        def set_action_key(self, key): self.action_key = key
        def set_toggle_key(self, key): self.toggle_key = key
        def set_mode(self, toggle: bool): self.mode_toggle = toggle

        def send_press(self):
            try:
                if self.action_key.startswith("mouse_"):
                    btn = self.action_key.split("_")[1]
                    mouse.press(button=btn if btn in ["left","right","middle","x","x2"] else "left")
                else:
                    keyboard.press(self.action_key)
                self.is_holding = True
            except: pass

        def send_release(self):
            try:
                if self.action_key.startswith("mouse_"):
                    btn = self.action_key.split("_")[1]
                    mouse.release(button=btn if btn in ["left","right","middle","x","x2"] else "left")
                else:
                    keyboard.release(self.action_key)
                self.is_holding = False
            except: pass

        def loop(self):
            next_click = time.perf_counter()
            while True:
                if self.active and not is_roblox():
                    if self.is_holding: self.send_release()
                    self.active = False
                    next_click = time.perf_counter()
                    time.sleep(0.001)
                    continue

                if self.active and is_roblox():
                    now = time.perf_counter()
                    if now >= next_click:
                        self.send_press()
                        time.sleep(max(0.00005, 0.45 / self.kps))
                        self.send_release()
                        next_click = now + 1.0 / self.kps
                    else:
                        time.sleep(max(0.00005, next_click - now))
                else:
                    if self.is_holding: self.send_release()
                    time.sleep(0.008)
                    next_click = time.perf_counter()

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
                    pressed = (keyboard.is_pressed(key) if not key.startswith("mouse_") 
                              else mouse.is_pressed(button=key.split("_")[1] if key.split("_")[1] in ["left","right","middle","x","x2"] else "left"))
                    now = time.perf_counter()

                    if self.macro.mode_toggle:
                        if pressed and not self.last_state and now - self.last_toggle_time >= 0.12:
                            if is_roblox():
                                self.macro.active = not self.macro.active
                                if not self.macro.active and self.macro.is_holding:
                                    self.macro.send_release()
                            self.last_toggle_time = now
                    else:
                        should_active = pressed and is_roblox()
                        if self.macro.active and not should_active and self.macro.is_holding:
                            self.macro.send_release()
                        self.macro.active = should_active
                    self.last_state = pressed
                except:
                    pass
                time.sleep(0.004)

    class Overlay(QWidget):
        def __init__(self, macro):
            super().__init__()
            self.macro = macro
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFixedSize(200,50)
            self.label = QLabel("Tush Off", self)
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setFixedSize(200,50)
            self.label.setStyleSheet("font-size:20px;font-weight:bold;color:red;background:rgba(0,0,0,180);border-radius:10px;")
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_overlay)
            self.timer.start(35)

        def update_overlay(self):
            if not is_roblox():
                self.hide()
                return
            self.show()
            if self.macro.active:
                self.label.setText("Tush On")
                self.label.setStyleSheet("font-size:20px;font-weight:bold;color:lime;background:rgba(0,0,0,180);border-radius:10px;")
            else:
                self.label.setText("Tush Off")
                self.label.setStyleSheet("font-size:20px;font-weight:bold;color:red;background:rgba(0,0,0,180);border-radius:10px;")
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            self.move(x, 50)

    class UI(QWidget):
        def __init__(self):
            super().__init__()
            self.version = CURRENT_VERSION
            self.macro = Macro()
            self.listener = ToggleListener(self.macro)
            self.listener.start()
            self.listening = False
            self.drag_pos = None
            self.init_ui()
            self.overlay = Overlay(self.macro)

        def init_ui(self):
            self.setFixedSize(400, 310)
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setWindowTitle("Tush Clash Macro")
            self.setWindowIcon(QIcon("icon.png"))

            layout = QVBoxLayout(self)
            layout.setContentsMargins(20,20,20,20)
            layout.setSpacing(15)

            title = QLabel(f"Tush Clash Macro - {self.version}")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size:24px;font-weight:bold;color:white;")
            layout.addWidget(title)

            layout.addWidget(QLabel("KPS"))
            self.kps_input = QLineEdit(str(self.macro.kps))
            self.kps_input.setStyleSheet(self.input_style())
            self.kps_input.setFixedHeight(40)
            self.kps_input.textChanged.connect(lambda t: self.macro.set_kps(t))
            layout.addWidget(self.kps_input)

            layout.addWidget(QLabel("Action Key"))
            self.action = QComboBox()
            self.action.addItems(["f","e","space","q","r","t","mouse_left","mouse_right"])
            self.action.setFixedHeight(40)
            self.action.setStyleSheet(self.input_style())
            self.action.currentTextChanged.connect(self.macro.set_action_key)
            layout.addWidget(self.action)

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

        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton: self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
        def mouseMoveEvent(self, event):
            if self.drag_pos and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_pos)
        def mouseReleaseEvent(self, event): self.drag_pos = None

        def set_hotkey(self):
            if self.listening: return
            self.listening = True
            self.hotkey_btn.setText("PRESIONA TECLA O BOTÓN...")

            def detect():
                while self.listening:
                    try:
                        for btn in ["left","right","middle","x","x2"]:
                            if mouse.is_pressed(button=btn):
                                self.apply_hotkey(f"mouse_{btn}")
                                return
                        e = keyboard.read_event(suppress=False)
                        if e.event_type == keyboard.KEY_DOWN:
                            self.apply_hotkey(e.name)
                            return
                    except:
                        pass
                    time.sleep(0.0008)
            threading.Thread(target=detect, daemon=True).start()

        def apply_hotkey(self, key):
            self.macro.set_toggle_key(key)
            display = key.upper() if not key.startswith("mouse_") else f"MOUSE {key.split('_')[1].upper()}"
            self.hotkey_btn.setText(display)
            self.listening = False

        def paintEvent(self, event):
            p = QPainter(self)
            p.fillRect(self.rect(), QColor("#000000"))

    ui = UI()
    ui.show()
    sys.exit(app.exec_())
