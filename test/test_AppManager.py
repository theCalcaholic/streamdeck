from pathlib import Path
import unittest
import json
from unittest.mock import Mock, patch
from streamdeck.kiosk import AppManager
from streamdeck.config import Configuration
from streamdeck.config.FirefoxConfig import FirefoxConfig
from streamdeck.config.AppConfig import AppConfig
from tempfile import TemporaryDirectory
from dataclasses import asdict

TEST_CONFIG = Configuration(config_path="/tmp", apps=[], firefox_profile_prefix='ff-prefix-',
                            firefox_config=FirefoxConfig(command=['/bin/firefox'],
                                                         config_path='/home/streamdeck/.mozilla/firefox'))


def _get_is_dir_mocked(dirs: list[str]):
    def is_dir(path: Path):
        return str(path) in dirs
    return is_dir


class TestAppManager(unittest.TestCase):

    def setUp(self) -> None:
        self.test_config_dir = TemporaryDirectory("streamdeck")
        self.ff_config_dir = TemporaryDirectory("firefox")
        self.test_config = TEST_CONFIG.load(json.loads(TEST_CONFIG.to_json()), self.test_config_dir.name)
        self.test_config.firefox_config = FirefoxConfig(command=self.test_config.firefox_config.command,
                                                        config_path=self.ff_config_dir.name)
        self.app_manager = AppManager(self.test_config)

    def tearDown(self) -> None:
        self.test_config_dir.cleanup()
        self.ff_config_dir.cleanup()

    def test_get_unique_profile_uid(self):
        app_uid = 'testapp'
        self.app_manager.profile_exists = Mock()
        self.app_manager.profile_exists.side_effect = [True, True, False]
        self.assertEqual(f'{self.test_config.firefox_profile_prefix}{app_uid}1',
                         self.app_manager.get_unique_profile_uid(app_uid))

    def test_profile_exists(self):
        with patch('streamdeck.kiosk.Path.is_dir',
                   new=_get_is_dir_mocked([f'{self.ff_config_dir.name}/myprofile'])):
            self.app_manager = AppManager(config=self.test_config)

            self.assertTrue(self.app_manager.profile_exists("myprofile"))
            self.assertFalse(self.app_manager.profile_exists("missingprofile"))

    @patch('streamdeck.kiosk.AppManager.install_app')
    def test_add_app(self, mock_install_app: Mock):
        app_name = 'myapp'
        app_url = 'https://media.ccc.de'

        expected_path = Path(self.ff_config_dir.name) / f'{self.test_config.firefox_profile_prefix}{app_name}'

        self.app_manager.add_app(app_name, app_url, hide_adress_bar=True)
        matching_apps = [app for app in self.test_config.apps if app.name == app_name]
        self.assertEqual(1, len(matching_apps))
        self.assertEqual(app_url, matching_apps[0].url)
        self.assertEqual(str(expected_path), matching_apps[0].firefox_profile)
        mock_install_app.assert_called_once_with(0)

    def test_install_app(self):
        app_name = 'myapp'
        app_url = 'https://media.ccc.de'
        profile_path = Path(self.ff_config_dir.name) / f'{self.test_config.firefox_profile_prefix}{app_name}'

        self.app_manager.config.apps.append(AppConfig(app_name, app_url, str(profile_path), hide_address_bar=True))
        print(asdict(self.app_manager.config.apps[0]))

        self.app_manager.install_app(0)

        self.assertTrue(profile_path.exists())
        self.assertTrue((profile_path / 'chrome/userChrome.css').is_file())


