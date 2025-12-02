import cv2
import numpy as np

class ColorDetector:
    def __init__(self, color_ranges, min_area=1000):

        self.color_ranges = color_ranges
        self.min_area = min_area

    def detect_colors(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detections = []

        for color, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Remove noise with morphological operations
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= self.min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detections.append((color, x, y, w, h))
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self._bgr_color(color), 2)
                    cv2.putText(frame, f"{color} ({int(area)})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, self._bgr_color(color), 2)

        return frame, detections

    def _bgr_color(self, color_name):
        colors = {
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0)
        }
        return colors.get(color_name.lower(), (255, 255, 255))
