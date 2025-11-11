"""
video_stream.py - Módulo de streaming de video para el dashboard

Maneja la captura y visualización de video desde distintas fuentes:
- Streaming HLS (HTTP Live Streaming)
- Cámara USB local
- Streaming RTSP
"""

import cv2
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

class VideoStreamThread(QThread):
    """Thread separado para captura de video sin bloquear la UI"""
    
    # Señal para enviar frames a la UI
    frame_ready = pyqtSignal(QImage)
    # Señal para reportar errores
    error_occurred = pyqtSignal(str)
    # Señal para reportar estado de conexión
    connection_status = pyqtSignal(bool)
    
    def __init__(self, source, width=640, height=480, fps=30):
        """
        Inicializa el thread de video
        
        Args:
            source: URL del stream, índice de cámara (0, 1...), o ruta de archivo
            width: Ancho del frame
            height: Alto del frame
            fps: Frames por segundo deseados
        """
        super().__init__()
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None
        self.running = False
        
    def run(self):
        """Bucle principal de captura de video"""
        try:
            # Intentar abrir la fuente de video
            self.capture = cv2.VideoCapture(self.source)
            
            # Configurar propiedades de captura
            if isinstance(self.source, int):  # Cámara USB
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            
            if not self.capture.isOpened():
                self.error_occurred.emit("No se pudo abrir la fuente de video")
                self.connection_status.emit(False)
                return
            
            self.running = True
            self.connection_status.emit(True)
            
            # Bucle de captura
            frame_count = 0
            while self.running:
                ret, frame = self.capture.read()
                
                if not ret:
                    self.error_occurred.emit("Frame no recibido - Reconectando...")
                    # Intentar reconectar
                    self.capture.release()
                    self.capture = cv2.VideoCapture(self.source)
                    if not self.capture.isOpened():
                        self.connection_status.emit(False)
                        break
                    continue
                
                # Redimensionar frame si es necesario
                if frame.shape[1] != self.width or frame.shape[0] != self.height:
                    frame = cv2.resize(frame, (self.width, self.height))
                
                # Convertir BGR (OpenCV) a RGB (Qt)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Crear QImage
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(
                    rgb_frame.data,
                    w, h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888
                )
                
                # Emitir señal con el frame
                self.frame_ready.emit(qt_image)
                
                frame_count += 1
                
                # Control de FPS (aproximado)
                self.msleep(int(1000 / self.fps))
                
        except Exception as e:
            self.error_occurred.emit(f"Error en captura de video: {str(e)}")
            self.connection_status.emit(False)
        
        finally:
            self.cleanup()
    
    def stop(self):
        """Detiene el thread de captura"""
        self.running = False
        self.wait()  # Esperar a que termine el thread
    
    def cleanup(self):
        """Libera recursos de video"""
        if self.capture is not None:
            self.capture.release()
            self.capture = None


class VideoStream:
    """
    Clase principal para manejo de streaming de video
    Integra el thread de captura con la UI
    """
    
    def __init__(self, video_label, config):
        """
        Inicializa el stream de video
        
        Args:
            video_label: QLabel donde se mostrará el video
            config: Diccionario con configuración (source, width, height, fps)
        """
        self.video_label = video_label
        self.config = config
        self.thread = None
        self.is_running = False
        
        # Callbacks opcionales
        self.on_error = None
        self.on_connection_change = None
    
    def start(self):
        """Inicia el streaming de video"""
        if self.is_running:
            print("[VIDEO] Stream ya está ejecutándose")
            return False
        
        # Crear y configurar thread
        self.thread = VideoStreamThread(
            source=self.config.get("source", 0),
            width=self.config.get("width", 640),
            height=self.config.get("height", 480),
            fps=self.config.get("fps", 30)
        )
        
        # Conectar señales
        self.thread.frame_ready.connect(self.update_frame)
        self.thread.error_occurred.connect(self.handle_error)
        self.thread.connection_status.connect(self.handle_connection_status)
        
        # Iniciar thread
        self.thread.start()
        self.is_running = True
        
        print(f"[VIDEO] Stream iniciado desde: {self.config.get('source', 'desconocido')}")
        return True
    
    def stop(self):
        """Detiene el streaming de video"""
        if not self.is_running:
            return
        
        if self.thread:
            self.thread.stop()
            self.thread = None
        
        self.is_running = False
        print("[VIDEO] Stream detenido")
    
    def update_frame(self, qt_image):
        """
        Actualiza el frame en el QLabel
        
        Args:
            qt_image: QImage con el frame a mostrar
        """
        if self.video_label:
            # Escalar imagen para ajustar al label manteniendo proporción
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
    
    def handle_error(self, error_message):
        """
        Maneja errores del stream
        
        Args:
            error_message: Mensaje de error
        """
        print(f"[VIDEO ERROR] {error_message}")
        if self.on_error:
            self.on_error(error_message)
    
    def handle_connection_status(self, connected):
        """
        Maneja cambios en el estado de conexión
        
        Args:
            connected: True si está conectado, False si no
        """
        status = "conectado" if connected else "desconectado"
        print(f"[VIDEO] Estado: {status}")
        if self.on_connection_change:
            self.on_connection_change(connected)
    
    def is_connected(self):
        """Retorna True si el stream está activo"""
        return self.is_running and self.thread and self.thread.isRunning()
    
    def take_snapshot(self, filename="snapshot.jpg"):
        """
        Captura una imagen del frame actual
        
        Args:
            filename: Nombre del archivo donde guardar
        
        Returns:
            True si se guardó correctamente, False si no
        """
        if not self.video_label.pixmap():
            print("[VIDEO] No hay frame para capturar")
            return False
        
        try:
            pixmap = self.video_label.pixmap()
            pixmap.save(filename)
            print(f"[VIDEO] Snapshot guardado: {filename}")
            return True
        except Exception as e:
            print(f"[VIDEO ERROR] No se pudo guardar snapshot: {e}")
            return False


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def test_video_source(source, timeout=5):
    """
    Prueba si una fuente de video es accesible
    
    Args:
        source: URL o índice de cámara
        timeout: Tiempo máximo de espera en segundos
    
    Returns:
        True si la fuente es accesible, False si no
    """
    try:
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout * 1000)
        
        if not cap.isOpened():
            cap.release()
            return False
        
        # Intentar leer un frame
        ret, _ = cap.read()
        cap.release()
        
        return ret
    except Exception as e:
        print(f"[VIDEO] Error probando fuente: {e}")
        return False


def get_available_cameras():
    """
    Detecta cámaras USB disponibles en el sistema
    
    Returns:
        Lista de índices de cámaras disponibles
    """
    available = []
    for i in range(10):  # Probar primeros 10 índices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available


def get_video_info(source):
    """
    Obtiene información de una fuente de video
    
    Args:
        source: URL o índice de cámara
    
    Returns:
        Diccionario con información del video o None si falla
    """
    try:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            return None
        
        info = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(cap.get(cv2.CAP_PROP_FPS)),
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        cap.release()
        return info
    except Exception as e:
        print(f"[VIDEO] Error obteniendo info: {e}")
        return None


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso standalone (sin PyQt)
    Para probar: python video_stream.py
    """
    
    from config import VIDEO_SOURCE, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS
    
    print("=== Test de Video Stream ===")
    print(f"Fuente: {VIDEO_SOURCE}")
    
    # Probar accesibilidad
    print("Probando accesibilidad de la fuente...")
    if test_video_source(VIDEO_SOURCE):
        print("✅ Fuente accesible")
    else:
        print("❌ Fuente no accesible")
        exit(1)
    
    # Obtener información
    info = get_video_info(VIDEO_SOURCE)
    if info:
        print(f"Info del video: {info}")
    
    # Captura simple para test
    print("\nIniciando captura (presiona 'q' para salir)...")
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la fuente")
        exit(1)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame no recibido")
            break
        
        frame_count += 1
        
        # Mostrar contador de frames
        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        cv2.imshow("Video Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n✅ Test completado. Frames procesados: {frame_count}")