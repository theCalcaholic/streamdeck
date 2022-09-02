import unittest
from unittest.mock import NonCallableMagicMock, patch, Mock
from streamdeck.config.util import find_binary, find_flatpak, is_valid_command
from subprocess import CompletedProcess
import os
from pathlib import Path


DUMMY_USER_HOME = '/home/streamdeck'


def _gen_is_valid_command_mock(valid_command: list[str]):
    def m_is_valid_command(cmd: list[str]):
        return cmd == valid_command
    return m_is_valid_command


def _gen_is_file_mocked(files: list[str]):
    def is_file(path: Path):
        return str(path) in files
    return is_file


class TestUtilFunctions(unittest.TestCase):

    def setUp(self) -> None:
        self.patchers = []
        expanduser_patcher = patch('streamdeck.config.util.expanduser')
        expanduser_mock = expanduser_patcher.start()
        expanduser_mock.return_value = DUMMY_USER_HOME
        self.patchers.append(expanduser_patcher)

    def tearDown(self) -> None:
        for patcher in self.patchers:
            patcher.stop()

    @patch('streamdeck.config.util.is_valid_command',
           new=_gen_is_valid_command_mock(['flatpak', 'run', '--user', 'org.mozilla.firefox']))
    def test_find_firefox_flatpak_user(self):
        command, config_path = find_flatpak("org.mozilla.firefox")
        self.assertEqual(["flatpak", "run", "--user", "org.mozilla.firefox"], command)
        self.assertEqual(f"{DUMMY_USER_HOME}/.var/app/org.mozilla.firefox", config_path)

    @patch('streamdeck.config.util.is_valid_command',
           new=_gen_is_valid_command_mock(['flatpak', 'run', '--system', 'org.mozilla.firefox']))
    def test_find_firefox_flatpak_system(self):
        command, config_path = find_flatpak("org.mozilla.firefox")
        self.assertEqual(["flatpak", "run", "--system", "org.mozilla.firefox"], command)
        self.assertEqual(f"{DUMMY_USER_HOME}/.var/app/org.mozilla.firefox", config_path)

    @patch('streamdeck.config.util.is_valid_command', new=_gen_is_valid_command_mock(['/bin/firefox']))
    @patch('streamdeck.config.util.which')
    def test_find_firefox_native(self, which_mock: Mock):
        which_mock.return_value = '/bin/firefox'
        command = find_binary("firefox")
        self.assertEqual(['/bin/firefox'], command)

    @patch('streamdeck.config.util.Path.is_file', new=_gen_is_file_mocked(['/bin/valid']))
    @patch('streamdeck.config.util.os.access')
    def test_is_valid_command_native(self, mock_os_access: Mock):
        mock_os_access.return_value = True

        self.assertTrue(is_valid_command(['/bin/valid']))
        mock_os_access.assert_called_with('/bin/valid', os.X_OK)

    @patch('streamdeck.config.util.Path.is_file', new=_gen_is_file_mocked(['flatpak']))
    @patch('streamdeck.config.util.os.access')
    @patch('streamdeck.config.util.which')
    @patch('streamdeck.config.util.subprocess.run')
    def test_is_valid_command_flatpak(self, mock_subprocess_run: Mock, mock_which: Mock, mock_os_access: Mock):
        mock_os_access.return_value = True
        mock_which.return_value = '/bin/flatpak'
        sp_run_result = NonCallableMagicMock(spec=CompletedProcess)
        sp_run_result.returncode = 0
        mock_subprocess_run.return_value = sp_run_result

        self.assertTrue(is_valid_command(['flatpak', 'run', '--user', 'org.mozilla.firefox']))
        mock_subprocess_run.assert_called_once()
        mock_subprocess_run.assert_called_with(['flatpak', 'info', '--user', 'org.mozilla.firefox'])
