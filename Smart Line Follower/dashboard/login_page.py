from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt6.QtCore import Qt
import os

class LoginPage(QWidget):
    def __init__(self, cfg, login_callback):
        super().__init__()
        self.cfg = cfg
        self.login_callback = login_callback  # Función que se ejecuta al hacer login exitoso
        self.init_ui()

    def init_ui(self):
        self.setAutoFillBackground(True)
        self.set_background_color(self.cfg["colors"]["background"])

        # Contenedor principal con límite de ancho
        main_container = QWidget()
        main_container.setMaximumWidth(500)
        
        # Layout del formulario
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Logo o imagen superior (opcional)
        bg_login = self.cfg["images"].get("background_login", "")
        if bg_login and os.path.exists(bg_login):
            logo_label = QLabel()
            pixmap = QPixmap(bg_login).scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            form_layout.addWidget(logo_label)
        
        # Título
        title_label = QLabel("Smart Line Follower Dashboard")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.cfg['colors']['text']}; padding: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Inicia sesión para continuar")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet(f"color: {self.cfg['colors']['secondary']}; padding-bottom: 20px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(subtitle_label)

        # Campo Usuario
        user_label = QLabel("Usuario:")
        user_label.setStyleSheet(f"color: {self.cfg['colors']['text']}; font-size: 14px;")
        form_layout.addWidget(user_label)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingresa tu usuario")
        self.user_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.cfg['colors']['panel']};
                color: {self.cfg['colors']['text']};
                border: 2px solid {self.cfg['colors']['secondary']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.cfg['colors']['accent']};
            }}
        """)
        form_layout.addWidget(self.user_input)

        # Campo Contraseña
        pass_label = QLabel("Contraseña:")
        pass_label.setStyleSheet(f"color: {self.cfg['colors']['text']}; font-size: 14px;")
        form_layout.addWidget(pass_label)
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Ingresa tu contraseña")
        self.pass_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.cfg['colors']['panel']};
                color: {self.cfg['colors']['text']};
                border: 2px solid {self.cfg['colors']['secondary']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.cfg['colors']['accent']};
            }}
        """)
        # Permitir login con Enter
        self.pass_input.returnPressed.connect(self.login_action)
        form_layout.addWidget(self.pass_input)

        # Checkbox Recordarme
        self.remember_cb = QCheckBox("Recordar mi sesión")
        self.remember_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {self.cfg['colors']['text']};
                font-size: 13px;
                padding: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {self.cfg['colors']['secondary']};
                background-color: {self.cfg['colors']['panel']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.cfg['colors']['accent']};
                border: 2px solid {self.cfg['colors']['accent']};
            }}
        """)
        form_layout.addWidget(self.remember_cb)

        # Botón Iniciar Sesión
        login_btn = QPushButton("Iniciar Sesión")
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.cfg['colors']['accent']};
                color: {self.cfg['colors']['text']};
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.cfg['colors']['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {self.cfg['colors']['panel']};
            }}
        """)
        login_btn.clicked.connect(self.login_action)
        form_layout.addWidget(login_btn)
        
        # Info adicional
        info_label = QLabel("Credenciales por defecto: admin / 1234")
        info_label.setStyleSheet(f"color: {self.cfg['colors']['secondary']}; font-size: 11px; padding-top: 20px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(info_label)

        main_container.setLayout(form_layout)

        # Layout horizontal para centrar
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(main_container)
        h_layout.addStretch(1)

        # Layout vertical para centrar verticalmente
        v_layout = QVBoxLayout()
        v_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        v_layout.addStretch(1)

        self.setLayout(v_layout)

    def set_background_color(self, hex_color):
        """Establece el color de fondo del widget"""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(hex_color))
        self.setPalette(palette)

    def login_action(self):
        """Valida credenciales e inicia sesión"""
        user = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        remember = self.remember_cb.isChecked()

        # Validación simple (expandible a base de datos)
        if user == "admin" and password == "1234":
            # Limpiar campos
            self.pass_input.clear()
            # Llamar callback de éxito
            self.login_callback(remember)
        else:
            QMessageBox.warning(
                self, 
                "Error de autenticación", 
                "Usuario o contraseña incorrectos.\n\nIntenta con: admin / 1234"
            )
            self.pass_input.clear()
            self.pass_input.setFocus()