from tkinter import *
from tkinter import messagebox
import time

tk = Tk()
app_running = True

size_canvas_x = 600
size_canvas_y = 600


def on_closing():
    global app_running
    if messagebox.askokcancel("Выход из игры", "Хотите выйти из игры?"):
        app_running = False
        tk.destroy()


tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Игра Морской Бой")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
canvas = Canvas(tk, width=size_canvas_x, height=size_canvas_y, bd=0, highlightthickness=0)
canvas.create_rectangle(0, 0, size_canvas_x, size_canvas_y, fill="white")
canvas.pack()
tk.update()

while app_running:
    if app_running:
        tk.update_idletasks()
        tk.update()
    time.sleep(0.005)
