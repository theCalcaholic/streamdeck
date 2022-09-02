from kivy.app import App
from kivy.uix.widget import Widget


class SDRootWidget(Widget):
    pass


class StreamDeckApp(App):
    def build(self):
        return SDRootWidget()


if __name__ == '__main__':
    StreamDeckApp().run()
