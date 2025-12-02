import cv2

class CameraModule:    
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_opened = False
        
    def open(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"Error: No se pudo abrir la cámara {self.camera_index}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        self.is_opened = True
        print(f"Cámara {self.camera_index} abierta correctamente")
        return True
    
    def read_frame(self):
        if not self.is_opened:
            print("Advertencia: La cámara no está abierta")
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))
        
        return ret, frame
    
    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print("Cámara cerrada correctamente")
    
    def __del__(self):
        self.close()