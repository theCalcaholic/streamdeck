#!/usr/bin/env python3


def run():
    from .gui import StreamDeckApp, config, app_manager
    print(config)
    StreamDeckApp().run()


if __name__ == '__main__':
    run()

