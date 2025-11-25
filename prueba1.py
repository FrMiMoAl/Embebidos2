# ========================================
# app_deteccion_uart_email.py
# Detector de marcadores + UART + alerta por correo
# ========================================

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from detector_yolo import DetectorYOLO
from manejador_camara import ManejadorCamara
from comunicacion_uart import ComunicacionUART

# ----------------------------------------
# CONFIGURACIÓN YOLO + UART
# ----------------------------------------
MODELO = "runs_marker/yolov8n_markers5/weights/best.pt"
CONFIANZA = 0.5
CAMARA = 0
PUERTO_SERIAL = "/dev/ttyAMA0"  # o "/dev/serial0" según tu configuración
BAUDRATE = 115200

# ----------------------------------------
# CONFIGURACIÓN CORREO
# ----------------------------------------
GMAIL_USER = "gabriel.palomeque@ucb.edu.bo"
GMAIL_PASSWORD = "aapu lkiq rchz uuwr"  # Pon aquí tu contraseña de aplicación de Gmail
DESTINATARIO = "franco.morales@ucb.edu.bo"

ASUNTO_ALERTA = "Alerta Raspi 5"
MENSAJE_ALERTA = "No hay marcadores detectados en la cámara."

# Tiempo mínimo entre correos (segundos)
EMAIL_COOLDOWN = 5
# Tiempo de espera inicial antes de activar alertas (segundos)
INITIAL_WAIT = 5


def enviar_alerta_correo():
    """
    Envía un correo de alerta indicando que no hay marcadores detectados.
    """
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = DESTINATARIO
    msg["Subject"] = ASUNTO_ALERTA

    msg.attach(MIMEText(MENSAJE_ALERTA, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, DESTINATARIO, msg.as_string())
        server.quit()
        print("📧 Alerta enviada por correo (no hay marcadores).")
    except Exception as e:
        print("⚠ Error al enviar correo:", e)


def main():
    print("=== Detector de Marcadores + UART + Correo ===\n")

    uart = None
    camara = None

    # Para evitar correos repetidos
    alerta_enviada = False
    last_email_time = 0.0  # último instante en que se mandó un correo

    try:
        # Inicializar componentes
        detector = DetectorYOLO(MODELO, CONFIANZA)
        camara = ManejadorCamara(CAMARA)
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)

        print("\n✓ Sistema listo")
        print(f"Esperando {INITIAL_WAIT} segundos antes de activar alertas...\n")

        # Espera inicial para estabilizar cámara / detección
        time.sleep(INITIAL_WAIT)

        print("Alertas activas. Presiona 'q' o ESC para salir.\n")

        # Bucle principal
        while True:
            # Leer frame
            frame = camara.leer_frame()
            if frame is None:
                print("[!] No se pudo leer frame de la cámara. Saliendo...")
                break

            # Detectar marcadores
            detecciones, conteos = detector.detectar(frame)

            # ----------------------------------------
            # LÓGICA DE ALERTA POR CORREO CON COOLDOWN
            # ----------------------------------------
            now = time.time()

            if len(detecciones) == 0:
                # No hay marcadores
                # Se envía correo solo si:
                # 1) No se ha enviado ya por esta "ronda"  O  ha pasado el cooldown
                # 2) Ha pasado el tiempo mínimo entre correos
                if (not alerta_enviada or (now - last_email_time) >= EMAIL_COOLDOWN) and \
                   (now - last_email_time) >= EMAIL_COOLDOWN:
                    print("⚠ No se detectan marcadores. Enviando alerta por correo...")
                    enviar_alerta_correo()
                    alerta_enviada = True
                    last_email_time = now
            else:
                # Si vuelven a aparecer marcadores, reseteamos la bandera
                alerta_enviada = False
            # ----------------------------------------

            # Enviar conteos por UART a la Pico
            uart.enviar_conteos(conteos)

            # Dibujar detecciones
            frame = detector.dibujar_detecciones(frame, detecciones)

            # Mostrar conteos en la imagen
            frame = camara.mostrar_conteos(frame, conteos)

            # Mostrar frame
            camara.mostrar_frame(frame, "Detector + UART + Correo")

            # Verificar salida por teclado
            if camara.verificar_tecla_salida():
                print("Tecla de salida detectada. Cerrando...")
                break

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario (Ctrl+C).")
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        if uart is not None:
            uart.cerrar()
        if camara is not None:
            camara.cerrar()
        print("✓ Programa finalizado")


if __name__ == "__main__":
    main()
