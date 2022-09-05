import json
import unittest
from .common import initialize_test_environment, TEST_USER, TEST_USER_HOME
import vdf
from pathlib import Path

from streamdeck.steam import Shortcuts
from streamdeck.config import AppConfig, FirefoxConfig


class TestShortcuts(unittest.TestCase):

    def setUp(self) -> None:
        self.test_config_dir, self.ff_config_dir, self.steam_config_dir, self.test_config = initialize_test_environment()

        self.shortcuts_data = {
            'shortcuts': {
                '0': {
                    'AppName': 'myapp',
                    'Exe': '"/bin/firefox"',
                    'StartDir': f'"{TEST_USER_HOME}"',
                    'LaunchOptions': '--profile /tmp/streamdeck-myapp https://media.ccc.de',
                    'AllowDesktopConfig': 1,
                    'AllowOverlay': 1,
                    'openvr': 0,
                    'Devkit': 0,
                    'DevkitGameID': '',
                    'DevkitOverrideAppID': 0,
                    'FlatpakAppID': '',
                    'tags': {'0': 'StreamDeck', '1': '/tmp/streamdeck-myapp'},
                    'collections': {'0': 'StreamDeck'}
                },
                '1': {
                    'AppName': 'myotherapp',
                    'Exe': '"/bin/firefox"',
                    'StartDir': f'"{TEST_USER_HOME}"',
                    'LaunchOptions': '--profile /tmp/streamdeck-myotherapp https://blog.ccc.de',
                    'AllowDesktopConfig': 1,
                    'AllowOverlay': 1,
                    'openvr': 0,
                    'Devkit': 0,
                    'DevkitGameID': '',
                    'DevkitOverrideAppID': 0,
                    'FlatpakAppID': '',
                    'tags': {'0': 'StreamDeck', '1': '/tmp/streamdeck-myotherapp'},
                    'collections': {'0': 'StreamDeck'}
                }
            }
        }
        self.shortcuts_path = Path(self.steam_config_dir.name) / 'shortcuts.vdf'
        with self.shortcuts_path.open('wb') as f:
            vdf.binary_dump(self.shortcuts_data, f)
        self.app_1 = AppConfig('myapp', 'https://media.ccc.de', '/tmp/streamdeck-myapp', hide_address_bar=True)
        self.app_2 = AppConfig('myotherapp', 'https://blog.ccc.de', '/tmp/streamdeck-myotherapp', hide_address_bar=True)

    def tearDown(self) -> None:
        for d in self.test_config_dir, self.ff_config_dir, self.steam_config_dir:
            d.cleanup()

    def test_get_app_shortcut(self):
        shortcuts = Shortcuts(self.shortcuts_data)
        app_shortcut = shortcuts[self.app_1]
        self.assertEqual(self.app_1.name, app_shortcut["AppName"])

    def test_update_app_shortcut(self):
        shortcuts = Shortcuts(self.shortcuts_data)
        new_app = AppConfig('mynewapp', 'https://videos.ccc.de', '/tmp/streamdeck-mynewapp', hide_address_bar=True)
        shortcuts[self.app_1] = new_app.to_shortcut(FirefoxConfig(command=['/bin/firefox'],
                                                                  config_path='/home/streamdeck/.mozilla/firefox'))

        self.assertEqual('mynewapp', shortcuts[new_app]['AppName'])
        self.assertRaises(KeyError, lambda: shortcuts[self.app_1])

    def test_add_app_shortcut(self):
        raise NotImplementedError

    def test_context_manager(self):
        new_app = AppConfig('mynewapp', 'https://videos.ccc.de', '/tmp/streamdeck-mynewapp', hide_address_bar=True)
        with Shortcuts(self.shortcuts_data, self.shortcuts_path) as s:
            s[new_app] = {
                'AppName': 'mynewapp',
                'Exe': '"/bin/firefox"',
                'StartDir': f'"{TEST_USER_HOME}"',
                'LaunchOptions': '--profile /tmp/streamdeck-mynewapp https://videos.ccc.de',
                'AllowDesktopConfig': 1,
                'AllowOverlay': 1,
                'openvr': 0,
                'Devkit': 0,
                'DevkitGameID': '',
                'DevkitOverrideAppID': 0,
                'FlatpakAppID': '',
                'tags': {'0': 'StreamDeck', '1': '/tmp/streamdeck-mynewapp'},
                'collections': {'0': 'StreamDeck'}
            }

        with self.shortcuts_path.open('rb') as f:
            shortcuts_data_new = vdf.binary_load(f)

        self.assertTrue(any(
            ('/tmp/streamdeck-mynewapp' in s['tags'].values()) for s in shortcuts_data_new['shortcuts'].values()))

        def contextmanager_without_path():
            with Shortcuts(self.shortcuts_data):
                print("This shouldn't work")

        self.assertRaises(ValueError, contextmanager_without_path)

    def test_load(self):
        raise NotImplementedError

    def test_dump(self):
        raise NotImplementedError
