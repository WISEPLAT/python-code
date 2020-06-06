## install GhostScript to fix error magick.exe: FailedToExecuteCommand `"gswin32c.exe"
## use portable ImageMagick-7.0.10-16-portable-Q16-x64 to convert images
from tkinter import *
tk = Tk()
canvas = Canvas(tk, width=1280, height=768)
canvas.pack()

canvas.create_rectangle(50,50,900,500,fill="red")
canvas.create_oval(400,400,700,700,fill="yellow")

tk.update()

canvas.postscript(file="my_drawing.ps", colormode="color")

import subprocess
cmd = r'C:\Users\user123\Desktop\p6\ImageMagick-7.0.10-16-portable-Q16-x64\magick.exe C:\Users\user123\Desktop\p6\my_drawing.ps C:\Users\user123\Desktop\p6\my_drawing.png'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
result = p.communicate()[0]
print(result.decode('cp866'))
