import cv2
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('''- Посмотрите, пожалуйста, мой принтер.
- А что с ним?
- Да захожу на сайт, читаю анекдоты — смешно, распечатываю — не смешно.
- Посмотрите, пожалуйста, мой принтер.
- А что с ним?
- Да захожу на сайт, читаю анекдоты — смешно, распечатываю — не смешно.
''')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode2.jpg", "JPEG")

img_qrcode = Image.open("qrcode2.jpg")
decoded = decode(img_qrcode)
print(decoded[0].data.decode("utf-8"))

#img_qrcode = cv2.imread("qrcode2.jpg")
#detector = cv2.QRCodeDetector()
#data, bbox, clear_qrcode = detector.detectAndDecode(img_qrcode)
#print(data)
#print(bbox)
#cv2.imshow("rez", clear_qrcode)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
