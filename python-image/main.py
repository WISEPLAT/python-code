from tkinter import *
from tkinter import messagebox

def on_closing():
    if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
        tk.destroy()

tk = Tk()
tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Приложение")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
canvas = Canvas(tk, width=900, height=600, bd=0, highlightthickness=0)
canvas.pack()

our_image = PhotoImage(file = "ramka.png")
our_image = our_image.subsample(5, 5)
our_label = Label(tk)
our_label.image = our_image
our_label['image'] = our_label.image
our_label.place(x = 20, y = 20)

our_image_1 = PhotoImage(file = "ramka.png")
our_image_1 = our_image_1.subsample(5, 5)
img_id0 = canvas.create_image(450, 300, anchor='nw', image = our_image_1)
img_id1 = canvas.create_image(470, 330, anchor='nw', image = our_image_1)

from PIL import Image, ImageTk
our_image2 = Image.open("ramka.png")
our_image2 = our_image2.resize((400, 220), Image.ANTIALIAS)
our_image2 = ImageTk.PhotoImage(our_image2)
our_label2 = Label(image = our_image2)
our_label2.image = our_image2
our_label2.place(x = 450, y = 20)

our_image2_2 = Image.open("ramka.png")
our_image2_2 = our_image2_2.resize((220, 220), Image.ANTIALIAS)
our_image2_2 = ImageTk.PhotoImage(our_image2_2)
img_id = canvas.create_image(20, 300, anchor='nw', image = our_image2_2)
img_id2 = canvas.create_image(40, 330, anchor='nw', image = our_image2_2)



tk.mainloop()
