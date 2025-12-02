import cv2
import numpy as np

def detect_color(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # RED color range
    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 100, 100])
    red_upper2 = np.array([179, 255, 255])

    # GREEN color range
    green_lower = np.array([35, 100, 100])
    green_upper = np.array([85, 255, 255])

    # BLUE color range
    blue_lower = np.array([100, 100, 100])
    blue_upper = np.array([130, 255, 255])


    mask_red = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    mask_green = cv2.inRange(hsv, green_lower, green_upper)
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)

    # Count how many pixels are in the mask
    red_pixels = cv2.countNonZero(mask_red)
    green_pixels = cv2.countNonZero(mask_green)
    blue_pixels = cv2.countNonZero(mask_blue)


    print("Color detection results:")
    if red_pixels > 0:
        print("Red detected")
    if green_pixels > 0:
        print("Green detected")
    if blue_pixels > 0:
        print("Blue detected")
    if red_pixels == green_pixels == blue_pixels == 0:
        print("No color detected.")

detect_color("colors/red.png")


'''
Send from tiva:
r: {red_pixels}, g: {green_pixels}, b: {blue_pixels}\n


'''