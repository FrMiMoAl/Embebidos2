import cv2
import numpy as np
import os


folder = "colors"

output_folder = "grayscale_colors"
os.makedirs(output_folder)


def rgb_to_grayscale(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return gray


for filename in os.listdir(folder):
    path = os.path.join(folder, filename)
    img = cv2.imread(path)

    gray_img = rgb_to_grayscale(img)

    cv2.imwrite(f"{output_folder}/gray_{filename}", gray_img)
    
    pixel_value = gray_img[50, 50]
    print(f"{filename}: Grayscale value = {pixel_value}")
