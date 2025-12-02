import cv2

class Video_Capture:
    def __init__(self, camera) -> None:
        self.camera = camera
        self.displayed = False
        self.mode = 'bgr' 

    def display_camera(self):
        self.displayed = True
        self.camera_visualization()

    def stop_display(self):
        self.displayed = False
        self.camera.release()
        cv2.destroyAllWindows()

    def camera_visualization(self):

        while self.displayed:
            check, frame = self.camera.read()
            if not check:
                print("Error: Cannot read frame from camera.")
                break

            if self.mode == 'gray':
                frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                frame_display = frame

            cv2.imshow("Camera Feed", frame_display)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:          # Esc key
                self.stop_display()
            elif key == ord('g'):
                self.mode = 'gray'
                print("Gray.")
            elif key == ord('r'):
                self.mode = 'rgb'
                print("RGB.")



if __name__ == "__main__":
    camera = cv2.VideoCapture(0)
    camera_object = Video_Capture(camera)
    camera_object.display_camera()
