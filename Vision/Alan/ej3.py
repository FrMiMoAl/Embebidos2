"""
HSV stands for Hue, Saturation, Value
Its a way of representing colors closer to how humans perceive them:

Hue: The type of color, measured in degrees

Saturation: The intensity or purity of the color (0 = gray, 255 = vivid color).

Value: The brightness of the color (0 = black, 255 = bright).
"""

import cv2
import numpy as np
import os

class ColorConverter:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original = cv2.imread(image_path)

    def to_hsv(self):
        hsv = cv2.cvtColor(self.original, cv2.COLOR_BGR2HSV)
        return hsv

    def to_grayscale(self):
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        return gray

    def show(self, image, title="Image"):
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



converter = ColorConverter("colors/red.png")

hsv_img = converter.to_hsv()
gray_img = converter.to_grayscale()

converter.show(converter.original, "Original")
converter.show(hsv_img, "HSV")
converter.show(gray_img, "Grayscale")