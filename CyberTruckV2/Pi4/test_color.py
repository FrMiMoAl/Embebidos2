import cv2
from color_detector import ColorDetector

# Define HSV color ranges
color_ranges = {
    # if needed calibrate these values for your environment
    "red": [(170, 130, 230), (180, 210, 255)],
    "green": [(52, 97, 90), (86, 255, 255)],
    "blue": [(100, 100, 180), (125, 230, 255)]
}


detector = ColorDetector(color_ranges)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    result_frame, detections = detector.detect_colors(frame)
    print("Detections:", detections)
    cv2.imshow("Color Detection", result_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



def send_serial(pwm1, pwm2, servo ):

    cad = "100,100,50 "
    pwm1 = cad  
    pass