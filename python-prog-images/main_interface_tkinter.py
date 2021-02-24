import os
# in terminal run command: pip install pillow
from PIL import Image as IMG_PIL

def resize_images_in_folder(directory = 'm:\\my_super_files_test_resize\\', resize_in_percent = 50, resize_x_to_min = 0, resize_y_to_min = 0):
    #directory = 'm:\\my_super_files_test_resize\\'

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



from tkinter import *
from tkinter import messagebox
from tkinter import filedialog


def on_closing():
    if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
        tk.destroy()


tk = Tk()
tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Мое приложение для изменения фотографий")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
#tk.iconbitmap("bomb-3175208_640.ico")

# canvas = Canvas(tk, width=600, height=600, highlightthickness=0)
# canvas.pack()

def select_folder_path():
    global mydir
    mydir = filedialog.askdirectory()
    selected_folder.configure(text=mydir)

def run_resize():
    #messagebox.showinfo("Python", percent.get() + " " + resize_x.get()+ " " + resize_y.get() + " " +mydir)
    resize_images_in_folder(mydir+"/", int(percent.get()), int(resize_x.get()), int(resize_y.get()))
    messagebox.showinfo("Фотки обработаны!!!", "Проверьте папку))))")

mydir = ""
percent = StringVar()
resize_x = StringVar()
resize_y = StringVar()

percent_label = Label(text="Percent, %:")
resize_x_label = Label(text="Resize by X to:")
resize_y_label = Label(text="Resize by Y to:")
selected_folder = Label(text="Please select folder!!!")

percent_label.grid(row=0, column=0, sticky="w")
resize_x_label.grid(row=1, column=0, sticky="w")
resize_y_label.grid(row=2, column=0, sticky="w")
selected_folder.grid(row=3, column=1, sticky="w")

percent_entry = Entry(textvariable=percent)
resize_x_entry = Entry(textvariable=resize_x)
resize_y_entry = Entry(textvariable=resize_y)

percent_entry.grid(row=0, column=1, padx=5, pady=5)
resize_x_entry.grid(row=1, column=1, padx=5, pady=5)
resize_y_entry.grid(row=2, column=1, padx=5, pady=5)

select_folder_button = Button(text="Select folder", command=select_folder_path)
select_folder_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")

run_button = Button(text="Run resize", command=run_resize)
run_button.grid(row=4, column=1, padx=5, pady=5, sticky="e")


tk.mainloop()
