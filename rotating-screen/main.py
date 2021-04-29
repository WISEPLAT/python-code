#pip install opencv-python pyautogui Pillow pywin32
import pyautogui, cv2, numpy, random

cv2.waitKey(1000)

image_screenshot = pyautogui.screenshot()
_array_image = numpy.array(image_screenshot)
image = cv2.cvtColor(_array_image, cv2.COLOR_RGB2BGR)

cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty("window",cv2.WND_PROP_TOPMOST,cv2.WND_PROP_TOPMOST)

import win32api
import win32con

def mouse_evt(event, x, y, flags, param):
    # Mouse is Moving
    if event == cv2.EVENT_MOUSEMOVE:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_ARROW))

cv2.setMouseCallback("window", mouse_evt)

cv2.imshow("window", image)

_width = _array_image.shape[1] #width
_height = _array_image.shape[0] #height
_columns = 40
_step = _width // _columns
_move_down_by = 5
_key = 0
while _key != 27:
    _array_image = numpy.flip(_array_image)
    image = cv2.cvtColor(_array_image, cv2.COLOR_RGB2BGR)
    cv2.imshow("window", image)
    _key = cv2.waitKey(100)

cv2.destroyAllWindows()
