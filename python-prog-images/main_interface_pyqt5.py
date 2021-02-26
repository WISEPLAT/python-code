import os
# in terminal run command: pip install pillow
from PIL import Image as IMG_PIL


def resize_images_in_folder(directory='m:\\my_super_files_test_resize\\', resize_in_percent=50, resize_x_to_min=0,
                            resize_y_to_min=0):
    # directory = 'm:\\my_super_files_test_resize\\'

    # only one value from three you should set !!!
    # resize_in_percent = 50  # percent to resize images in folder
    # resize_x_to_min = 0  # min width in pixels to resize images in folder
    # resize_y_to_min = 0  # min height in pixels to resize images in folder
    if resize_x_to_min + resize_y_to_min != 0:
        resize_in_percent = False

    with os.scandir(path=directory) as it:
        for entry in it:
            if not entry.is_file():
                print("dir:\t" + entry.name)
            else:
                print("file:\t" + entry.name)
                img_obj = IMG_PIL.open(directory + entry.name)
                width_size = height_size = 0
                if resize_in_percent:
                    percent = 100 / resize_in_percent
                    width_size = int(float(img_obj.size[0]) / percent)
                    height_size = int(float(img_obj.size[1]) / percent)
                else:
                    if resize_x_to_min:
                        delta = resize_x_to_min / float(img_obj.size[0])
                        width_size = int(float(img_obj.size[0]) * delta)
                        height_size = int(float(img_obj.size[1]) * delta)
                    else:
                        delta = resize_y_to_min / float(img_obj.size[1])
                        width_size = int(float(img_obj.size[0]) * delta)
                        height_size = int(float(img_obj.size[1]) * delta)
                img_obj = img_obj.resize((width_size, height_size), IMG_PIL.ANTIALIAS)
                img_obj.save(directory + entry.name)


# in terminal run command: pip install pyqt5
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox

print(os.path.realpath(__file__))
dirname, filename = os.path.split(os.path.realpath(__file__))
print(dirname)
Form, Window = uic.loadUiType(dirname + "\\1.ui")

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()

mydir = ""

from PyQt5.QtWidgets import QFileDialog

def on_click_select_folder():
    global mydir
    print("b1 clicked!")
    dialog = QFileDialog()
    mydir = dialog.getExistingDirectory(window, 'Select directory')
    print(mydir)
    form.label_4.setText(mydir)

def on_click_resize_images():
    percent = form.lineEdit.text()
    resize_x = form.lineEdit_2.text()
    resize_y = form.lineEdit_3.text()
    resize_images_in_folder(mydir+"/", int(percent), int(resize_x), int(resize_y))
    QMessageBox.information(window, "Фотки обработаны!!!", "Проверьте папку))))", QMessageBox.Ok)

form.pushButton.clicked.connect(on_click_select_folder)
form.pushButton_2.clicked.connect(on_click_resize_images)

app.exec_()
