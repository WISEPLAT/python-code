from tkinter import *
from tkinter import messagebox

from PIL import Image, ImageTk

tk = Tk()
app_running = True

size_canvas_x = 500
size_canvas_y = 500
s_x = s_y = 8
#s_y = 8
step_x = size_canvas_x // s_x  # шаг по горизонтали
step_y = size_canvas_y // s_y  # шаг по вертикали
size_canvas_x = step_x * s_x
size_canvas_y = step_y * s_y

def on_closing():
    global app_running
    if messagebox.askokcancel("Выход из игры", "Хотите выйти из игры?"):
        app_running = False
        tk.destroy()


tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Игра Шахматы")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
canvas = Canvas(tk, width=size_canvas_x, height=size_canvas_y, bd=0,
                highlightthickness=0)

canvas.pack()
tk.update()

def draw_table():
    for i in range(0, s_x + 1):
        canvas.create_line(step_x * i, 0, step_x * i, size_canvas_y)
    for i in range(0, s_y + 1):
        canvas.create_line(0, step_y * i, size_canvas_x, step_y * i)

draw_table()

canvas1 = Canvas(tk, width=step_x-6, height=step_y-6)
canvas1.place(x=2, y=step_y+2, anchor=NW)
our_image2_2 = Image.open("chess-ferz.png")
our_image2_2 = our_image2_2.resize((step_x-2, step_y-2), Image.ANTIALIAS)
our_image2_2 = ImageTk.PhotoImage(our_image2_2)
img_id = canvas1.create_image(0, 0, anchor='nw', image = our_image2_2)

canvas2 = Canvas(tk, width=step_x-6, height=step_y-6)
canvas2.place(x=step_x+2, y=step_y+2, anchor=NW)
our_image2_3 = Image.open("chess-ladya.png")
our_image2_3 = our_image2_3.resize((step_x-2, step_y-2), Image.ANTIALIAS)
our_image2_3 = ImageTk.PhotoImage(our_image2_3)
img_id = canvas2.create_image(0, 0, anchor='nw', image = our_image2_3)



def drag(event):
    #print(event.x_root, event.y_root)
    mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
    #print(mouse_x, mouse_y)
    event.widget.place(x=mouse_x, y=mouse_y, anchor=CENTER)

def release_obj(event):
    mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
    #print(mouse_x, mouse_y)
    ip_x = mouse_x // step_x
    ip_y = mouse_y // step_y
    # x_obj = event.widget.winfo_x()
    # y_obj = event.widget.winfo_y()
    # ip_x = x_obj // step_x
    # ip_y = y_obj // step_y
    #print(x_obj, y_obj)
    print(ip_x, ip_y)
    event.widget.place(x=ip_x*step_x+step_x//2, y=ip_y*step_y+step_y//2)

canvas1.bind("<B1-Motion>", drag)
canvas1.bind("<ButtonRelease-1>", release_obj)
canvas2.bind("<B1-Motion>", drag)
canvas2.bind("<ButtonRelease-1>", release_obj)


tk.mainloop()
