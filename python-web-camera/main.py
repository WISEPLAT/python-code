import cv2

cap = cv2.VideoCapture(1)

while True:
    ret, img = cap.read()
    cv2.imshow("camera", img)
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
