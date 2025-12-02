import cv2
import os
import numpy as np

folder = "colors"

for filename in os.listdir(folder):
    path = os.path.join(folder, filename)
    img = cv2.imread(path)

    colorpixel = img[50, 50]

    print(f"{filename}: BGR = {colorpixel}")
