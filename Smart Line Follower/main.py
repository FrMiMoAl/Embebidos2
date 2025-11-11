#!/usr/bin/env python3
"""
Smart Line Follower - Control Dashboard
Punto de entrada principal de la aplicación

Este módulo inicializa la aplicación PyQt6 y carga el dashboard manager.
"""

import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont

sys.path.append('dashboard')

def check_config_file():
    """Verifica que el archivo de configuración exista"""
    if not os.path.exists("cfg_dashboard.json"):
        print("[ERROR] No se encontró el archivo 'cfg_dashboard.json'")
        print("[INFO] Creando archivo de configuración por defecto...")
        
        default_config = {
            "colors": {
                "background": "#10232A",
                "panel": "#3D4D55",
                "text": "#D3C3B9",
                "accent": "#B58863",
                "secondary": "#A79E9C",
                "black": "#18161B"
            },
            "images": {
                "background_login": "assets/bg_login.jpg",
                "background_main": "assets/bg_main.jpg",
                "camera_placeholder": "assets/camera_placeholder.jpg",
                "arrow_up": "assets/arrow_up.png",
                "arrow_down": "assets/arrow_down.png",
                "arrow_left": "assets/arrow_left.png",
                "arrow_right": "assets/arrow_right.png",
                "arrow_up_active": "assets/arrow_up_active.png",
                "arrow_down_active": "assets/arrow_down_active.png",
                "arrow_left_active": "assets/arrow_left_active.png",
                "arrow_right_active": "assets/arrow_right_active.png",
                "function1": "assets/func1.png",
                "function2": "assets/func2.png",
                "function3": "assets/func3.png",
                "function4": "assets/func4.png",
                "icon": "assets/icon.png"
            }
        }
        
        try:
            with open("cfg_dashboard.json", "w") as f:
                json.dump(default_config, f, indent=4)
            print("[INFO] Archivo de configuración creado exitosamente")
        except Exception as e:
            print(f"[ERROR] No se pudo crear el archivo de configuración: {e}")
            return False
    
    return True

def main():
    """Función principal de la aplicación"""
    
    # Verificar archivo de configuración
    if not check_config_file():
        sys.exit(1)
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Line Follower Dashboard")
    app.setOrganizationName("YourOrganization")
    
    # Establecer fuente global
    font = QFont("Arial", 10)
    app.setFont(font)
    
    try:
        # Cargar configuración
        with open("cfg_dashboard.json", "r") as f:
            cfg = json.load(f)
        
        # Crear y mostrar dashboard manager
        #from dashboard import DashboardManager
        from dashboard_manager import DashboardManager
        manager = DashboardManager(cfg_path="cfg_dashboard.json")
        manager.show()
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except FileNotFoundError:
        QMessageBox.critical(
            None,
            "Error de configuración",
            "No se pudo encontrar el archivo 'cfg_dashboard.json'.\n"
            "Asegúrate de que el archivo existe en el directorio de la aplicación."
        )
        sys.exit(1)
    
    except json.JSONDecodeError as e:
        QMessageBox.critical(
            None,
            "Error de configuración",
            f"El archivo 'cfg_dashboard.json' contiene errores de formato:\n{str(e)}\n\n"
            "Verifica la sintaxis JSON del archivo."
        )
        sys.exit(1)
    
    except Exception as e:
        QMessageBox.critical(
            None,
            "Error Fatal",
            f"Ha ocurrido un error inesperado:\n{str(e)}"
        )
        print(f"[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()