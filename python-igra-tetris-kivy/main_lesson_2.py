from kivy.app import App
from kivy.uix.widget import Widget
from random import random as r
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE

class GridGame(Widget):
    def draw_grid(self, wid, TILE_W, TILE_H):
        with wid.canvas:
            for x in range(W):
                for y in range(H):
                    Color(r(), 1, 1, mode='hsv')
                    Rectangle(pos=(20+x*TILE_W, 20+y*TILE_H), size=(TILE_W, TILE_H))

class TetrisGame(Widget):
    my_grid = GridGame()


class TetrisApp(App):
    def build(self):
        Window.bind(on_resize=self.on_window_resize)
        return TetrisGame()

    def on_start(self):
        self._width = self.root.ids['game_layout'].width
        self._height = self.root.ids['game_layout'].height
        self._width_glass = self._width/20*12
        self._height_glass = self._height - 40

        TILE_W = self._width_glass / W
        TILE_H = self._height_glass / H

        self.root.my_grid.draw_grid(self.root.ids['game_layout_box'], TILE_W, TILE_H)

    def on_window_resize(self, window, width, height):
        self._width = self.root.ids['game_layout'].width
        self._height = self.root.ids['game_layout'].height
        self._width_glass = self._width/20*12
        self._height_glass = self._height - 40

        TILE_W = self._width_glass / W
        TILE_H = self._height_glass / H

        self.root.ids['game_layout_box'].canvas.clear()
        self.root.my_grid.draw_grid(self.root.ids['game_layout_box'], TILE_W, TILE_H)

if __name__ == '__main__':
    TetrisApp().run()
