import av
import cv2
import numpy as np

container = av.open("https://finder-blogging-married-chocolate.trycloudflare.com/cam/index.m3u8")

for frame in container.decode(video=0):
    img = frame.to_ndarray(format='bgr24')
    cv2.imshow("HLS Video", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
