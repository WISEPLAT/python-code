from tkinter import *
from tkinter import messagebox


def on_closing():
    if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
        tk.destroy()

def on_closing_2(this_window):
    if messagebox.askokcancel("Закрытие 2 окна", "Хотите закрыть 2 окно?"):
        print("Закрытие 2 окна - успешно!!!")
        this_window.destroy()


tk = Tk()
tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Мое приложение")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
# tk.iconbitmap("bomb-3175208_640.ico")

canvas = Canvas(tk, width=400, height=400, bg="red", highlightthickness=0)
canvas.pack()

def start_window_1():
    new_window_1 = Toplevel(tk)
    new_window_1.title("Мое окно 1")
    new_window_1.resizable(0, 0)
    new_window_1.wm_attributes("-topmost", 1)
    canvas_1 = Canvas(new_window_1, width=200, height=200, bg="yellow", highlightthickness=0)
    canvas_1.pack()
    canvas_1.create_rectangle(50, 50, 150, 150, fill="blue", outline="")


def start_window_2():
    new_window_2 = Toplevel(tk)
    new_window_2.title("Окно 2")
    new_window_2.resizable(0, 0)
    new_window_2.protocol("WM_DELETE_WINDOW", lambda this_window=new_window_2: on_closing_2(this_window))
    canvas_2 = Canvas(new_window_2, width=200, height=200, bg="green", highlightthickness=0)
    canvas_2.pack()
    canvas_2.create_oval(50, 50, 150, 150, fill="darkgreen", outline="")


b0 = Button(tk, text="Кнопка 1 окна", command=start_window_1)
b0.place(x=100, y=100)

b1 = Button(tk, text="Кнопка 2 окна", command=start_window_2)
b1.place(x=200, y=200)

# canvas.create_oval(100, 100, 300, 300, fill="yellow", outline="")
# canvas.create_oval(120, 120, 280, 280, fill="white", outline="")
#
# canvas.create_rectangle(400,100,500,500, fill="lightgreen")
# canvas.create_rectangle(420,120,480,480, fill="darkgreen", outline="")
#
# canvas.create_text(200,500,text="Hello World!", font=("Arial", 40),fill="white")


tk.mainloop()
