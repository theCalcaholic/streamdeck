import unittest
from unittest.mock import patch, Mock, NonCallableMagicMock
from streamdeck.config.SteamConfig import SteamConfig
from subprocess import CompletedProcess
from os import PathLike
from .common import TEST_USER_HOME


def _gen_is_valid_command_mock(valid_command: list[str]):
    def m_is_valid_command(cmd: list[str]):
        return cmd == valid_command
    return m_is_valid_command


def _gen_subprocess_run(cmds: dict[list[str], int]):
    def m_run(cmd):
        result = NonCallableMagicMock(spec=CompletedProcess)
        if cmd not in cmds:
            result.returncode = 1
        else:
            result.returncode = cmds[cmd]
        return result
    return m_run


def _gen_is_file_mocked(files: list[str]):
    def is_file(path: PathLike):
        return str(path) in files
    return is_file


class TestSteamConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.patchers = []
        expanduser_patcher = patch('streamdeck.config.SystemApplicationConfig.expanduser')
        expanduser_mock = expanduser_patcher.start()
        expanduser_mock.return_value = TEST_USER_HOME
        self.patchers.append(expanduser_patcher)

    def tearDown(self) -> None:
        for patcher in self.patchers:
            patcher.stop()

    @patch('streamdeck.config.SystemApplicationConfig.find_flatpak')
    @patch('streamdeck.config.SystemApplicationConfig.find_binary')
    def test_autodetect(self, find_binary_mock: Mock, find_flatpak_mock: Mock):

        # Case 3: No valid installation detected

        ff_native_cmd = ff_flatpak_cmd = None
        ff_native_config_path = f"{TEST_USER_HOME}"
        ff_flatpak_config_path = f"{TEST_USER_HOME}/.var/app/com.valvesoftware.Steam"

        find_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_binary_mock.return_value = ff_native_cmd

        ff_config = SteamConfig.autodetect()

        self.assertEqual(None, ff_config.command)
        self.assertEqual(None, ff_config.config_path)
        self.assertFalse(ff_config.is_flatpak)
        self.assertFalse(ff_config.autodetected)
        find_binary_mock.assert_called_once_with("steam")
        find_flatpak_mock.assert_called_once_with("com.valvesoftware.Steam")

        # Case 2: No flatpak but native installation detected

        ff_native_cmd = ['/bin/steam']

        find_flatpak_mock.reset_mock()
        find_binary_mock.reset_mock()
        find_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_binary_mock.return_value = ff_native_cmd

        ff_config = SteamConfig.autodetect()

        self.assertEqual(ff_native_cmd, ff_config.command)
        self.assertEqual(f"{ff_native_config_path}/.local/share/Steam", ff_config.config_path)
        self.assertFalse(ff_config.is_flatpak)
        self.assertTrue(ff_config.autodetected)

        # Case 3: Flatpak and Firefox installation detected (flatpak should take precedence)

        ff_flatpak_cmd = ['flatpak', 'run', '--user', 'com.valvesoftware.Steam']

        find_flatpak_mock.reset_mock()
        find_binary_mock.reset_mock()
        find_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_binary_mock.return_value = ff_native_cmd

        ff_config = SteamConfig.autodetect()

        self.assertEqual(ff_flatpak_cmd, ff_config.command)
        self.assertEqual(f"{ff_flatpak_config_path}/.local/share/Steam", ff_config.config_path)
        self.assertTrue(ff_config.is_flatpak)
        self.assertTrue(ff_config.autodetected)

    def test_library_paths(self):
        self.patchers[0].stop()
        steam_config = SteamConfig.autodetect()
        print(steam_config.library_paths)
