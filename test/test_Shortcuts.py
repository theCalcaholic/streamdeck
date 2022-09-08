import json
import unittest
from .common import initialize_test_environment, TEST_SHORTCUTS_DATA, TEST_USER_HOME, TEST_USER_ID, \
    setup_steam_shortcuts, TEST_APPS
import vdf
from pathlib import Path

from streamdeck.steam import Shortcuts
from streamdeck.config import AppConfig, FirefoxConfig


class TestShortcuts(unittest.TestCase):

    def setUp(self) -> None:
        self.test_config_dir, self.ff_config_dir, self.steam_config_dir, self.test_config = initialize_test_environment()

        self.shortcuts_data = TEST_SHORTCUTS_DATA
        self.shortcuts_path = setup_steam_shortcuts(TEST_USER_ID, self.steam_config_dir.name)
        [self.app1, self.app2] = TEST_APPS

    def tearDown(self) -> None:
        for d in self.test_config_dir, self.ff_config_dir, self.steam_config_dir:
            d.cleanup()

    def test_get_app_shortcut(self):
        shortcuts = Shortcuts(self.shortcuts_data, TEST_USER_ID)
        app_shortcut = shortcuts[self.app1]
        self.assertEqual(self.app1.name, app_shortcut["AppName"])

    def test_update_app_shortcut(self):
        shortcuts = Shortcuts(self.shortcuts_data, TEST_USER_ID)
        new_app = AppConfig('mynewapp', 'https://videos.ccc.de', '/tmp/streamdeck-mynewapp', hide_address_bar=True)
        shortcuts[self.app1] = new_app.to_shortcut(FirefoxConfig(command=['/bin/firefox'],
                                                                 config_path='/home/streamdeck/.mozilla/firefox'),
                                                   TEST_USER_ID)

        self.assertEqual('mynewapp', shortcuts[new_app]['AppName'])
        self.assertRaises(KeyError, lambda: shortcuts[self.app1])

    def test_add_app_shortcut(self):
        raise NotImplementedError

    def test_context_manager(self):
        new_app = AppConfig('mynewapp', 'https://videos.ccc.de', '/tmp/streamdeck-mynewapp', hide_address_bar=True)
        with Shortcuts(self.shortcuts_data, TEST_USER_ID, self.steam_config_dir.name) as s:
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
            with Shortcuts(self.shortcuts_data, TEST_USER_ID):
                print("This shouldn't work")

        self.assertRaises(ValueError, contextmanager_without_path)

    def test_load(self):
        raise NotImplementedError

    def test_dump(self):
        raise NotImplementedError
