from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtGui import QIcon
import json
import os

class DashboardManager(QMainWindow):
    def __init__(self, cfg_path="cfg_dashboard.json"):
        super().__init__()
        with open(cfg_path, "r") as f:
            self.cfg = json.load(f)
        
        self.setWindowTitle("Smart Line Follower - Control Dashboard")
        icon_path = self.cfg["images"].get("icon", "")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(f"background-color: {self.cfg['colors']['background']};")
        
        # Stack de páginas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Importar páginas
        from login_page import LoginPage
        from main_page import MainPage
        
        # Crear páginas
        self.login_page = LoginPage(self.cfg, self.on_login_success)
        self.main_page = MainPage(self.cfg, self.on_logout)
        
        # Agregar al stack
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_page)
        
        # IMPORTANTE: Deshabilitar el teclado de main_page por defecto
        self.main_page.release_keyboard_control()
        
        # Verificar si hay sesión guardada
        self.check_saved_session()
    
    def check_saved_session(self):
        """Verifica si existe una sesión guardada y válida"""
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session = json.load(f)
                    if session.get("remember", False):
                        # Iniciar sesión automáticamente
                        self.show_main()
                        return
        except:
            pass
        # Si no hay sesión guardada, mostrar login
        self.show_login()
    
    def show_login(self):
        """Muestra la página de login"""
        # CRÍTICO: Liberar el teclado de main_page si estaba capturado
        if hasattr(self, 'main_page'):
            self.main_page.release_keyboard_control()
        self.stacked_widget.setCurrentWidget(self.login_page)
        # Asegurar que el login tenga el foco para escribir
        self.login_page.setFocus()
        self.login_page.user_input.setFocus()
    
    def show_main(self):
        """Muestra la página principal"""
        # Configurar SSH si es necesario
        ssh_config = {
            "host": "raspberrypi.local",  # Cambiar según necesidad
            "port": 22,
            "username": "pi",
            "password": ""  # Se puede pedir o cargar de config
        }
        self.main_page.set_ssh_config(ssh_config)
        
        # Cambiar a página principal y activar captura de teclado
        self.stacked_widget.setCurrentWidget(self.main_page)
        self.main_page.activate_keyboard_control()
    
    def on_login_success(self, remember):
        """Callback cuando el login es exitoso"""
        # Guardar sesión
        try:
            with open("session.json", "w") as f:
                json.dump({"remember": remember}, f)
        except Exception as e:
            print(f"Error guardando sesión: {e}")
        
        # Cambiar a página principal
        self.show_main()
    
    def on_logout(self):
        """Callback cuando se cierra sesión"""
        # Limpiar sesión guardada
        try:
            with open("session.json", "w") as f:
                json.dump({"remember": False}, f)
        except:
            pass
        
        # Volver al login
        self.show_login()