import cv2

source = "https://finder-blogging-married-chocolate.trycloudflare.com/cam/index.m3u8"
cap = cv2.VideoCapture(source)

if not cap.isOpened():
    print("No se pudo abrir HLS")
    exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame no recibido")
        break

    cv2.imshow("HLS Video", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
