from pathlib import Path
import unittest
import json
from unittest.mock import Mock, patch
from streamdeck.kiosk import AppManager
from streamdeck.config import Configuration
from tempfile import TemporaryDirectory

TEST_CONFIG = Configuration(config_path="/tmp", apps=[], firefox_profile_prefix='ff-prefix-')


def _get_is_dir_mocked(dirs: list[str]):
    def is_dir(path: Path):
        return str(path) in dirs
    return is_dir


class TestAppManager(unittest.TestCase):

    def setUp(self) -> None:
        self.test_config_dir = TemporaryDirectory("streamdeck")
        self.test_config = TEST_CONFIG.load(json.loads(TEST_CONFIG.to_json()), str(self.test_config_dir))
        self.app_manager = AppManager(self.test_config)

    def tearDown(self) -> None:
        self.test_config_dir.cleanup()

    def test_get_unique_profile_uid(self):
        app_uid = 'testapp'
        self.app_manager.profile_exists = Mock()
        self.app_manager.profile_exists.side_effect = [True, True, False]
        self.assertEqual(f'{self.test_config.firefox_profile_prefix}{app_uid}1',
                         self.app_manager.get_unique_profile_uid(app_uid))

    @patch('streamdeck.kiosk.Path.is_dir',
           new=_get_is_dir_mocked([f'{TEST_CONFIG.config_path}/myprofile']))
    def test_profile_exists(self):
        self.assertTrue(self.app_manager.profile_exists("myprofile"))
        self.assertFalse(self.app_manager.profile_exists("missingprofile"))

    def test_add_page(self):
        app_name = 'myapp'
        app_url = 'https://media.ccc.de'

        expected_path = Path(str(self.test_config_dir)) / f'{self.test_config.firefox_profile_prefix}{app_name}'

        self.app_manager.add_app(app_name, app_url, hide_adress_bar=True)
        self.assertTrue(expected_path.exists())
        matching_apps = [app for app in self.test_config.apps if app.name == app_name]
        self.assertEqual(1, len(matching_apps))
        self.assertEqual(app_url, matching_apps[0].url)


