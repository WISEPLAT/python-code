import os
import random

directory = 'C:\\some_imgs_for_test\\'
files = os.listdir(directory)
print(files)

from tkinter import *
from tkinter import messagebox

# pip install pillow
from PIL import Image, ImageTk

def on_closing():
    if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
        tk.destroy()


tk = Tk()
tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Мое приложение")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
#tk.iconbitmap("bomb-3175208_640.ico")

canvas = Canvas(tk, width=1000, height=700, bg="red", highlightthickness=0)
canvas.pack()

random.shuffle(files)

for img in files:
    img_obj = Image.open(directory+img)
    box = 500
    wide_size = (box/float(img_obj.size[0]))
    height_size = int((float(img_obj.size[1])*float(wide_size)))
    img_obj = img_obj.resize((box, height_size), Image.ANTIALIAS)
    img_obj = ImageTk.PhotoImage(img_obj)
    our_label2 = Label(image=img_obj)
    our_label2.image = img_obj
    our_label2.place(x=random.randint(0,600), y=random.randint(0,400))


tk.mainloop()
