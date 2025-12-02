import cv2
import os
from abc import ABC, abstractmethod

class VideoCaptureBase(ABC):
    @abstractmethod
    def capture_frame(self):
        pass

    @abstractmethod
    def process_frame(self, frame):
        pass

class Video_Capture(VideoCaptureBase):
    def __init__(self, camera, save_dir="Captures") -> None:
        self.camera = camera
        self.displayed = False
        self.mode = 'bgr'
        self.save_dir = save_dir
        self.img_counter = 1

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def display_camera(self):
        self.displayed = True
        self.camera_visualization()

    def stop_display(self):
        self.displayed = False
        self.camera.release()
        cv2.destroyAllWindows()


    def camera_visualization(self):
        while self.displayed:
            ret, frame = self.camera.read()

            frame_display = self.process_frame(frame)

            cv2.imshow("Camera Feed", frame_display)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # Esc
                self.stop_display()
                break
            elif key == ord('g'):
                self.mode = 'gray'
                print("Gray mode")
            elif key == ord('r'):
                self.mode = 'rgb'
                print(" RGB mode")
            elif key == ord('c'):
                self.capture_frame(frame)

    def capture_frame(self, frame):
        img_name = os.path.join(self.save_dir, f"image{self.img_counter}.jpg")
        cv2.imwrite(img_name, frame)
        print(f"{img_name} saved!")
        self.img_counter += 1

    def process_frame(self, frame):
        if self.mode == 'gray':
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            return frame

    def post_process_last_image(self):
        if self.img_counter <= 1:
            print("No images captured.")
            return

        last_image_path = os.path.join(self.save_dir, f"image{self.img_counter - 1}.jpg")
        img = cv2.imread(last_image_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape

        quadrants = {
            "Top Left": img[0:h//2, 0:w//2],
            "Top Right": img[0:h//2, w//2:w],
            "Bottom Left": img[h//2:h, 0:w//2],
            "Bottom Right": img[h//2:h, w//2:w]
        }

        for name, quad in quadrants.items():
            cv2.imshow(name, quad)

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    camera = cv2.VideoCapture(0)
    cam_obj = Video_Capture(camera)
    cam_obj.display_camera()

    cam_obj.post_process_last_image()
