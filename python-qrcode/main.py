import cv2
import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('Изучаем мир ИТ')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode2.jpg", "JPEG")

img_qrcode = cv2.imread("qrcode2.jpg")
detector = cv2.QRCodeDetector()

data, bbox, clear_qrcode = detector.detectAndDecode(img_qrcode)
print(data)
print(bbox)
cv2.imshow("rez", clear_qrcode)
cv2.waitKey(0)
cv2.destroyAllWindows()
