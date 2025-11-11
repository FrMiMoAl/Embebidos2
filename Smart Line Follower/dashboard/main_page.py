from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QTextEdit, QFrame)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
import os

class MainPage(QWidget):
    def __init__(self, cfg, logout_callback=None):
        super().__init__()
        self.cfg = cfg
        self.logout_callback = logout_callback
        self.ssh_config = None
        self.keyboard_active = False
        
        # Estado de teclas presionadas
        self.keys_pressed = {}
        
        # Video stream (se inicializa después)
        self.video_stream = None
        
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.cfg['colors']['background']}; 
                color: {self.cfg['colors']['text']};
            }}
        """)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel izquierdo (video + consola)
        left_panel = QVBoxLayout()
        left_panel.addLayout(self.create_video_panel())
        left_panel.addWidget(self.create_console_panel())
        
        # Panel derecho (controles)
        right_panel = self.create_control_panel()
        
        main_layout.addLayout(left_panel, stretch=3)
        main_layout.addLayout(right_panel, stretch=1)
        
        self.setLayout(main_layout)

    # ==================== PANEL DE VIDEO ====================
    def create_video_panel(self):
        """Crea el panel superior con el video/cámara"""
        layout = QVBoxLayout()
        
        # Frame contenedor del video
        video_frame = QFrame()
        video_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.cfg['colors']['panel']};
                border-radius: 10px;
                border: 2px solid {self.cfg['colors']['secondary']};
            }}
        """)
        
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(10, 10, 10, 10)
        
        # Label para mostrar video
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(f"background-color: {self.cfg['colors']['black']}; border-radius: 8px;")
        
        # Cargar imagen placeholder
        bg_path = self.cfg["images"].get("camera_placeholder", "")
        if bg_path and os.path.exists(bg_path):
            pixmap = QPixmap(bg_path).scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(pixmap)
        
        # Botón Conectar superpuesto
        self.connect_btn = QPushButton("🎥 CONECTAR CÁMARA")
        self.connect_btn.setFixedSize(200, 60)
        self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.cfg['colors']['accent']};
                color: {self.cfg['colors']['text']};
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                border: 3px solid {self.cfg['colors']['text']};
            }}
            QPushButton:hover {{
                background-color: {self.cfg['colors']['secondary']};
                border: 3px solid {self.cfg['colors']['accent']};
            }}
            QPushButton:pressed {{
                background-color: {self.cfg['colors']['panel']};
            }}
        """)
        self.connect_btn.clicked.connect(self.connect_camera)
        
        video_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        video_frame.setLayout(video_layout)
        
        # Layout para superponer botón
        overlay_layout = QVBoxLayout()
        overlay_layout.addWidget(video_frame)
        
        # Posicionar botón en el centro del video
        button_container = QWidget()
        button_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.connect_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        
        layout.addWidget(video_frame)
        
        return layout

    def connect_camera(self):
        """
        ╔═══════════════════════════════════════════════════════════╗
        ║  🎯 PUNTO DE INTEGRACIÓN: INICIAR VIDEO/CÁMARA          ║
        ╚═══════════════════════════════════════════════════════════╝
        """
        self.video_label.clear()
        self.video_label.setStyleSheet(f"background-color: {self.cfg['colors']['black']}; border-radius: 8px;")
        self.connect_btn.hide()
        self.console_append("[SISTEMA] Conectando a cámara...", "info")
        
        try:
            # Importar módulos de video y configuración
            from video_stream import VideoStream
            from config import get_video_config
            
            # Obtener configuración de video
            video_config = get_video_config()
            self.console_append(f"[VIDEO] Fuente: {video_config['source']}", "info")
            
            # Crear instancia de video stream
            self.video_stream = VideoStream(self.video_label, video_config)
            
            # Configurar callbacks
            self.video_stream.on_error = lambda msg: self.console_append(f"[VIDEO ERROR] {msg}", "error")
            self.video_stream.on_connection_change = self.on_video_connection_change
            
            # Iniciar stream
            if self.video_stream.start():
                self.console_append("[VIDEO] Stream iniciado correctamente", "success")
            else:
                self.console_append("[VIDEO] No se pudo iniciar el stream", "error")
                self.connect_btn.show()
                
        except ImportError as e:
            self.console_append(f"[ERROR] Módulos no encontrados: {e}", "error")
            self.console_append("[INFO] Asegúrate de tener video_stream.py y config.py", "warning")
            self.connect_btn.show()
        except Exception as e:
            self.console_append(f"[ERROR] Error al conectar cámara: {e}", "error")
            self.connect_btn.show()
    
    def on_video_connection_change(self, connected):
        """Callback cuando cambia el estado de conexión del video"""
        if connected:
            self.status_led.setText("● Conectado")
            self.status_led.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 13px;")
            self.console_append("[SISTEMA] Cámara conectada", "success")
        else:
            self.status_led.setText("● Desconectado")
            self.status_led.setStyleSheet("color: #FF0000; font-weight: bold; font-size: 13px;")
            self.console_append("[SISTEMA] Cámara desconectada", "warning")

    # ==================== PANEL DE CONSOLA ====================
    def create_console_panel(self):
        """Crea el panel de consola/log SSH"""
        console_frame = QFrame()
        console_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.cfg['colors']['panel']};
                border-radius: 10px;
                border: 2px solid {self.cfg['colors']['secondary']};
            }}
        """)
        
        console_layout = QVBoxLayout()
        console_layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        console_title = QLabel("📟 Consola SSH - Raspberry Pi 4")
        console_title.setStyleSheet(f"""
            color: {self.cfg['colors']['accent']};
            font-weight: bold;
            font-size: 14px;
            padding: 5px;
        """)
        
        # Text Edit para la consola
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(180)
        self.console.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.cfg['colors']['black']};
                color: #00FF00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid {self.cfg['colors']['secondary']};
                border-radius: 5px;
                padding: 8px;
            }}
        """)
        
        self.console_append("[SISTEMA] Consola inicializada. Esperando conexión SSH...", "info")
        
        console_layout.addWidget(console_title)
        console_layout.addWidget(self.console)
        console_frame.setLayout(console_layout)
        
        return console_frame

    def console_append(self, message, msg_type="info"):
        """Añade mensajes a la consola con formato"""
        color_map = {
            "info": "#00BFFF",
            "success": "#00FF00",
            "warning": "#FFA500",
            "error": "#FF0000",
            "debug": "#FFD700"
        }
        color = color_map.get(msg_type, "#FFFFFF")
        self.console.append(f'<span style="color: {color};">{message}</span>')

    # ==================== PANEL DE CONTROL ====================
    def create_control_panel(self):
        """Crea el panel derecho con controles"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # === STATUS DEL VEHÍCULO ===
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.cfg['colors']['panel']};
                border-radius: 10px;
                border: 2px solid {self.cfg['colors']['secondary']};
                padding: 10px;
            }}
        """)
        
        status_layout = QVBoxLayout()
        
        status_title = QLabel("📊 Estado del Vehículo")
        status_title.setStyleSheet(f"color: {self.cfg['colors']['accent']}; font-weight: bold; font-size: 14px;")
        
        self.status_led = QLabel("● Desconectado")
        self.status_led.setStyleSheet("color: #FF0000; font-weight: bold; font-size: 13px;")
        
        self.kb_label = QLabel("⬆ 0 KB/s  |  ⬇ 0 KB/s")
        self.kb_label.setStyleSheet(f"color: {self.cfg['colors']['text']}; font-size: 12px;")
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_led)
        status_layout.addWidget(self.kb_label)
        status_frame.setLayout(status_layout)
        
        layout.addWidget(status_frame)
        
        # === CONTROLES DE MOVIMIENTO ===
        movement_frame = QFrame()
        movement_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.cfg['colors']['panel']};
                border-radius: 10px;
                border: 2px solid {self.cfg['colors']['secondary']};
                padding: 10px;
            }}
        """)
        
        movement_layout = QVBoxLayout()
        
        movement_title = QLabel("🎮 Control de Movimiento")
        movement_title.setStyleSheet(f"color: {self.cfg['colors']['accent']}; font-weight: bold; font-size: 14px;")
        movement_layout.addWidget(movement_title)
        
        # Flechas direccionales en grid
        arrows_grid = QGridLayout()
        arrows_grid.setSpacing(8)
        
        self.arrow_buttons = {}
        arrow_positions = {
            "up": (0, 1),
            "left": (1, 0),
            "down": (1, 1),
            "right": (1, 2)
        }
        
        for direction, (row, col) in arrow_positions.items():
            btn = self.create_arrow_button(direction)
            self.arrow_buttons[direction] = btn
            arrows_grid.addWidget(btn, row, col)
        
        movement_layout.addLayout(arrows_grid)
        movement_frame.setLayout(movement_layout)
        
        layout.addWidget(movement_frame)
        
        # === FUNCIONES ESPECIALES ===
        functions_frame = QFrame()
        functions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.cfg['colors']['panel']};
                border-radius: 10px;
                border: 2px solid {self.cfg['colors']['secondary']};
                padding: 10px;
            }}
        """)
        
        functions_layout = QVBoxLayout()
        
        functions_title = QLabel("⚡ Funciones Especiales")
        functions_title.setStyleSheet(f"color: {self.cfg['colors']['accent']}; font-weight: bold; font-size: 14px;")
        functions_layout.addWidget(functions_title)
        
        # Botones de funciones en grid 2x2
        func_grid = QGridLayout()
        func_grid.setSpacing(10)
        
        self.func_buttons = {}
        for i in range(1, 5):
            btn = self.create_function_button(i)
            self.func_buttons[i] = btn
            func_grid.addWidget(btn, (i-1)//2, (i-1)%2)
        
        functions_layout.addLayout(func_grid)
        functions_frame.setLayout(functions_layout)
        
        layout.addWidget(functions_frame)
        
        # === BOTÓN CERRAR SESIÓN ===
        logout_btn = QPushButton("🚪 Cerrar Sesión")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #8B0000;
                color: {self.cfg['colors']['text']};
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #A52A2A;
            }}
        """)
        logout_btn.clicked.connect(self.logout)
        
        layout.addWidget(logout_btn)
        layout.addStretch()
        
        return layout

    def create_arrow_button(self, direction):
        """Crea un botón de flecha direccional"""
        btn = QPushButton()
        btn.setFixedSize(70, 70)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.cfg['colors']['secondary']};
                border-radius: 8px;
                border: 2px solid {self.cfg['colors']['accent']};
            }}
            QPushButton:hover {{
                background-color: {self.cfg['colors']['accent']};
            }}
        """)
        
        # Cargar imagen
        img_path = self.cfg["images"].get(f"arrow_{direction}", "")
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
        else:
            # Flechas de texto como fallback
            symbols = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
            btn.setText(symbols.get(direction, "?"))
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 32px; color: {self.cfg['colors']['text']};")
        
        btn.pressed.connect(lambda: self.arrow_pressed(direction))
        btn.released.connect(lambda: self.arrow_released(direction))
        
        return btn

    def create_function_button(self, number):
        """Crea un botón de función especial"""
        btn = QPushButton()
        btn.setFixedSize(90, 90)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.cfg['colors']['secondary']};
                border-radius: 10px;
                border: 3px solid {self.cfg['colors']['accent']};
            }}
            QPushButton:hover {{
                background-color: {self.cfg['colors']['accent']};
                border: 3px solid {self.cfg['colors']['text']};
            }}
            QPushButton:pressed {{
                background-color: {self.cfg['colors']['panel']};
            }}
        """)
        
        img_path = self.cfg["images"].get(f"function{number}", "")
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(
                70, 70,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
        else:
            btn.setText(f"F{number}")
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 20px; font-weight: bold; color: {self.cfg['colors']['text']};")
        
        btn.clicked.connect(lambda: self.function_pressed(number))
        
        return btn

    # ==================== EVENTOS DE MOVIMIENTO ====================
    def arrow_pressed(self, direction):
        """
        ╔═══════════════════════════════════════════════════════════╗
        ║  🎯 PUNTO DE INTEGRACIÓN: MOVIMIENTO INICIADO           ║
        ╚═══════════════════════════════════════════════════════════╝
        Llamar función de control de motor cuando se presiona una dirección
        
        from motor_control import MotorController
        self.motor.move(direction, speed=100)
        """
        if direction in self.keys_pressed and self.keys_pressed[direction]:
            return  # Ya está presionada
        
        self.keys_pressed[direction] = True
        
        # Cambiar a imagen activa
        active_path = self.cfg["images"].get(f"arrow_{direction}_active", "")
        btn = self.arrow_buttons.get(direction)
        
        if btn and active_path and os.path.exists(active_path):
            pixmap = QPixmap(active_path).scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setStyleSheet(btn.styleSheet().replace(
                self.cfg['colors']['secondary'],
                self.cfg['colors']['accent']
            ))
        
        self.console_append(f"[MOVIMIENTO] Dirección: {direction.upper()} ACTIVADA", "success")
        
        # TODO: Llamar función de movimiento
        pass

    def arrow_released(self, direction):
        """
        ╔═══════════════════════════════════════════════════════════╗
        ║  🎯 PUNTO DE INTEGRACIÓN: MOVIMIENTO DETENIDO           ║
        ╚═══════════════════════════════════════════════════════════╝
        Detener motor cuando se suelta la dirección
        
        self.motor.stop(direction)
        """
        self.keys_pressed[direction] = False
        
        # Volver a imagen normal
        default_path = self.cfg["images"].get(f"arrow_{direction}", "")
        btn = self.arrow_buttons.get(direction)
        
        if btn and default_path and os.path.exists(default_path):
            pixmap = QPixmap(default_path).scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setStyleSheet(btn.styleSheet().replace(
                self.cfg['colors']['accent'],
                self.cfg['colors']['secondary']
            ))
        
        self.console_append(f"[MOVIMIENTO] Dirección: {direction.upper()} DESACTIVADA", "warning")
        
        # TODO: Llamar función de detención
        pass

    def function_pressed(self, number):
        """
        ╔═══════════════════════════════════════════════════════════╗
        ║  🎯 PUNTO DE INTEGRACIÓN: FUNCIÓN ESPECIAL              ║
        ╚═══════════════════════════════════════════════════════════╝
        Ejecutar función especial según el botón presionado
        
        from special_functions import execute_function
        execute_function(number)
        """
        self.console_append(f"[FUNCIÓN] Ejecutando función especial #{number}", "debug")
        
        # TODO: Implementar funciones especiales
        pass

    # ==================== CONTROL DE TECLADO ====================
    def activate_keyboard_control(self):
        """Activa la captura de teclado para esta página"""
        self.keyboard_active = True
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.grabKeyboard()
        self.setFocus()

    def release_keyboard_control(self):
        """Libera la captura de teclado"""
        self.keyboard_active = False
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        """Captura eventos de tecla presionada"""
        if not self.keyboard_active:
            return
        
        key_map = {
            Qt.Key.Key_W: "up",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_S: "down",
            Qt.Key.Key_Down: "down",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_D: "right",
            Qt.Key.Key_Right: "right"
        }
        
        if event.key() in key_map:
            direction = key_map[event.key()]
            if not event.isAutoRepeat():  # Evitar repeticiones automáticas
                self.arrow_pressed(direction)

    def keyReleaseEvent(self, event):
        """Captura eventos de tecla liberada"""
        if not self.keyboard_active:
            return
        
        key_map = {
            Qt.Key.Key_W: "up",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_S: "down",
            Qt.Key.Key_Down: "down",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_D: "right",
            Qt.Key.Key_Right: "right"
        }
        
        if event.key() in key_map:
            direction = key_map[event.key()]
            if not event.isAutoRepeat():
                self.arrow_released(direction)

    # ==================== SSH Y CONFIGURACIÓN ====================
    def set_ssh_config(self, config):
        """
        ╔═══════════════════════════════════════════════════════════╗
        ║  🎯 PUNTO DE INTEGRACIÓN: CONEXIÓN SSH                  ║
        ╚═══════════════════════════════════════════════════════════╝
        Establecer conexión SSH con Raspberry Pi
        
        import paramiko
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.connect(config['host'], config['port'], ...)
        """
        self.ssh_config = config
        self.console_append(f"[SSH] Configuración recibida: {config.get('host', 'N/A')}", "info")
        
        # TODO: Implementar conexión SSH real
        pass

    def logout(self):
        """Cierra sesión y vuelve al login"""
        # Detener video si está activo
        if self.video_stream and self.video_stream.is_running:
            self.console_append("[VIDEO] Deteniendo stream...", "info")
            self.video_stream.stop()
        
        self.release_keyboard_control()
        if self.logout_callback:
            self.logout_callback()
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        # Asegurarse de detener el video al cerrar
        if self.video_stream and self.video_stream.is_running:
            self.video_stream.stop()
        event.accept()