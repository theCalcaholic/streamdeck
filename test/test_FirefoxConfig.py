import os
import unittest
from unittest.mock import patch, Mock, NonCallableMagicMock
from streamdeck.config.FirefoxConfig import find_firefox_flatpak, find_firefox_native, is_valid_command, FirefoxConfig
from subprocess import CompletedProcess
from pathlib import Path


DUMMY_USER_HOME = '/home/streamdeck'


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
    def is_file(path: Path):
        return str(path) in files
    return is_file


class TestFirefoxConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.patchers = []
        expanduser_patcher = patch('streamdeck.config.FirefoxConfig.expanduser')
        expanduser_mock = expanduser_patcher.start()
        expanduser_mock.return_value = DUMMY_USER_HOME
        self.patchers.append(expanduser_patcher)

    def tearDown(self) -> None:
        for patcher in self.patchers:
            patcher.stop()

    @patch('streamdeck.config.FirefoxConfig.is_valid_command',
           new=_gen_is_valid_command_mock(['flatpak', 'run', '--user', 'org.mozilla.firefox']))
    def test_find_firefox_flatpak_user(self):
        command, config_path = find_firefox_flatpak()
        self.assertEqual(["flatpak", "run", "--user", "org.mozilla.firefox"], command)
        self.assertEqual(f"{DUMMY_USER_HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox", config_path)

    @patch('streamdeck.config.FirefoxConfig.is_valid_command',
           new=_gen_is_valid_command_mock(['flatpak', 'run', '--system', 'org.mozilla.firefox']))
    def test_find_firefox_flatpak_system(self):
        command, config_path = find_firefox_flatpak()
        self.assertEqual(["flatpak", "run", "--system", "org.mozilla.firefox"], command)
        self.assertEqual(f"{DUMMY_USER_HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox", config_path)

    @patch('streamdeck.config.FirefoxConfig.is_valid_command', new=_gen_is_valid_command_mock(['/bin/firefox']))
    @patch('streamdeck.config.FirefoxConfig.which')
    def test_find_firefox_native(self, which_mock: Mock):
        which_mock.return_value = '/bin/firefox'
        command, config_path = find_firefox_native()
        self.assertEqual(['/bin/firefox'], command)
        self.assertEqual(f"{DUMMY_USER_HOME}/.mozilla/firefox", config_path)

    @patch('streamdeck.config.FirefoxConfig.Path.is_file', new=_gen_is_file_mocked(['/bin/valid']))
    @patch('streamdeck.config.FirefoxConfig.os.access')
    def test_is_valid_command_native(self, mock_os_access: Mock):
        mock_os_access.return_value = True

        self.assertTrue(is_valid_command(['/bin/valid']))
        mock_os_access.assert_called_with('/bin/valid', os.X_OK)

    @patch('streamdeck.config.FirefoxConfig.Path.is_file', new=_gen_is_file_mocked(['flatpak']))
    @patch('streamdeck.config.FirefoxConfig.os.access')
    @patch('streamdeck.config.FirefoxConfig.which')
    @patch('streamdeck.config.FirefoxConfig.subprocess.run')
    def test_is_valid_command_flatpak(self, mock_subprocess_run: Mock, mock_which: Mock, mock_os_access: Mock):
        mock_os_access.return_value = True
        mock_which.return_value = '/bin/flatpak'
        sp_run_result = NonCallableMagicMock(spec=CompletedProcess)
        sp_run_result.returncode = 0
        mock_subprocess_run.return_value = sp_run_result

        self.assertTrue(is_valid_command(['flatpak', 'run', '--user', 'org.mozilla.firefox']))
        mock_subprocess_run.assert_called_once()
        mock_subprocess_run.assert_called_with(['flatpak', 'info', '--user', 'org.mozilla.firefox'])

    @patch('streamdeck.config.FirefoxConfig.find_firefox_flatpak')
    @patch('streamdeck.config.FirefoxConfig.find_firefox_native')
    def test_autodetect(self, find_ff_native_mock: Mock, find_ff_flatpak_mock: Mock):

        # Case 3: No valid installation detected

        ff_native_cmd = ff_flatpak_cmd = None
        ff_native_config_path = f"{DUMMY_USER_HOME}/.mozilla/firefox"
        ff_flatpak_config_path = f"{DUMMY_USER_HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox"

        find_ff_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_ff_native_mock.return_value = (ff_native_cmd, ff_native_config_path)

        ff_config = FirefoxConfig.autodetect()

        self.assertEqual(None, ff_config.command)
        self.assertEqual(None, ff_config.config_path)
        self.assertFalse(ff_config.is_flatpak)
        self.assertFalse(ff_config.autodetected)

        # Case 2: No flatpak but native installation detected

        ff_native_cmd = ['/bin/firefox']

        find_ff_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_ff_native_mock.return_value = (ff_native_cmd, ff_native_config_path)

        ff_config = FirefoxConfig.autodetect()

        self.assertEqual(ff_native_cmd, ff_config.command)
        self.assertEqual(ff_native_config_path, ff_config.config_path)
        self.assertFalse(ff_config.is_flatpak)
        self.assertTrue(ff_config.autodetected)

        # Case 3: Flatpak and Firefox installation detected (flatpak should take precedence)

        ff_flatpak_cmd = ['flatpak', 'run', '--user', 'org.mozilla.firefox']

        find_ff_flatpak_mock.return_value = (ff_flatpak_cmd, ff_flatpak_config_path)
        find_ff_native_mock.return_value = (ff_native_cmd, ff_native_config_path)

        ff_config = FirefoxConfig.autodetect()

        self.assertEqual(ff_flatpak_cmd, ff_config.command)
        self.assertEqual(ff_flatpak_config_path, ff_config.config_path)
        self.assertTrue(ff_config.is_flatpak)
        self.assertTrue(ff_config.autodetected)


