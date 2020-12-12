from tkinter import *
from tkinter import messagebox


def on_closing():
    if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
        tk.destroy()


tk = Tk()
tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Мое приложение")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
# tk.iconbitmap("bomb-3175208_640.ico")

canvas = Canvas(tk, width=600, height=600, highlightthickness=0)
canvas.pack()


def bg_color_red():
    canvas.configure(bg="red")
    id_button1.configure(bg="red", activebackground="red")
    label.configure(bg="red", activebackground="red")

def bg_color_yellow(event):
    canvas.configure(bg="yellow")
    id_button1.configure(bg="yellow", activebackground="yellow")
    label.configure(bg="yellow", activebackground="yellow")

our_button = PhotoImage(file="the-button-1692268_640.png")
our_button = our_button.subsample(2, 2)
# id_img1 = canvas.create_image(130,100, anchor="nw", image=our_button)
# Button(tk, image=our_button, highlightthickness=0, bd=0, command=lambda: print("Clicked!")).place(x=130, y=100)
#Button(tk, image=our_button, highlightthickness=0, bd=0, command=bg_color_red).place(x=130, y=100)
id_button1 = Button(tk, image=our_button, highlightthickness=0, bd=0, command=bg_color_red)
id_button1.place(x=130, y=100)

label = Label(tk, image=our_button)
label.place(x=130, y=300)
#label.bind("<Button-1>", lambda event: print("Click is OK!"))
label.bind("<Button-1>", bg_color_yellow)
label.bind("<Enter>", lambda event: label.place(x=132, y=302))
label.bind("<Leave>", lambda event: label.place(x=130, y=300))


tk.mainloop()
