from kivy.app import App
from kivy.uix.widget import Widget


class TetrisGame(Widget):
    pass


class TetrisApp(App):
    def build(self):
        return TetrisGame()


if __name__ == '__main__':
    TetrisApp().run()
