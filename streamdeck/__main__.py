#!/usr/bin/env python3


def run():
    import asyncio
    from .gui import StreamDeckApp, config, app_manager
    print(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(StreamDeckApp().async_run(async_lib='asyncio'))
    loop.close()


if __name__ == '__main__':
    run()

