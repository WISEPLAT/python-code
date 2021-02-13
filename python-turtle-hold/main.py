import turtle


def draw_circle_and_box(x, y, size):
    t.up()
    t.goto(x, y)
    t.down()
    t.color(0, 0, 1)
    t.begin_fill()
    t.forward(size)
    t.right(90)
    t.forward(size)
    t.right(90)
    t.forward(size)
    t.right(90)
    t.forward(size)
    t.right(90)
    t.end_fill()

    t.up()
    t.goto(x + size // 2, y - size)
    t.down()
    t.color(1, 1, 0)
    t.begin_fill()
    t.circle(size // 2)
    t.end_fill()


t = turtle.Pen()

x = int(input("Введите X: "))
y = int(input("Введите Y: "))
size = 300

draw_circle_and_box(x, y, size)

turtle.done()
#turtle.getscreen()._root.mainloop()
#turtle.Screen().mainloop()

# bad method!!!
# import time
# time.sleep(1000)

# bad method!!!
#input("Нажмите Enter!!!!")
