import unittest
from streamdeck.steam import Shortcuts
from streamdeck.config import AppConfig, FirefoxConfig

DUMMY_USER_HOME = '/home/streamdeck'


class TestShortcuts(unittest.TestCase):

    def setUp(self) -> None:

        shortcuts_data = {
            'shortcuts': {
                '0': {
                    'AppName': 'myapp',
                    'Exe': '"/bin/firefox"',
                    'StartDir': f'"{DUMMY_USER_HOME}"',
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
                    'StartDir': f'"{DUMMY_USER_HOME}"',
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
        self.shortcuts = Shortcuts(shortcuts_data)
        self.app_1 = AppConfig('myapp', 'https://media.ccc.de', '/tmp/streamdeck-myapp', hide_address_bar=True)
        self.app_2 = AppConfig('myotherapp', 'https://blog.ccc.de', '/tmp/streamdeck-myotherapp', hide_address_bar=True)

    def test_get_app_shortcut(self):

        app_shortcut = self.shortcuts[self.app_1]
        self.assertEqual(self.app_1.name, app_shortcut["AppName"])

    def test_set_app_shortcut(self):

        new_app = AppConfig('mynewapp', 'https://videos.ccc.de', '/tmp/streamdeck-mynewapp', hide_address_bar=True)
        self.shortcuts[self.app_1] = new_app.to_shortcut(FirefoxConfig(command=['/bin/firefox'],
                                                                       config_path='/home/streamdeck/.mozilla/firefox'))

        self.assertEqual('mynewapp', self.shortcuts[new_app]['AppName'])
        self.assertRaises(KeyError, lambda: self.shortcuts[self.app_1])




