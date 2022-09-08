import json
from tempfile import TemporaryDirectory
from pathlib import Path
import vdf
from os import PathLike

from streamdeck.config import Configuration, FirefoxConfig, SteamConfig, AppConfig


TEST_CONFIG = Configuration(config_path="/tmp", apps=[], firefox_profile_prefix='ff-prefix-',
                            steam_config=SteamConfig(command=['/bin/firefox'],
                                                     config_path='/home/streamdeck/.local/share/Steam'),
                            firefox_config=FirefoxConfig(command=['/bin/firefox'],
                                                         config_path='/home/streamdeck/.mozilla/firefox'))


TEST_USER = 'streamdeck'
TEST_USER_HOME = f'/home/{TEST_USER}'
TEST_USER_ID = '01234'

TEST_SHORTCUTS_DATA = {
    'shortcuts': {
        '0': {
            'AppName': 'myapp',
            'Exe': '"/bin/firefox"',
            'StartDir': f'"{TEST_USER_HOME}"',
            'LaunchOptions': f'--profile /tmp/streamdeck-myapp/{TEST_USER_ID} https://media.ccc.de',
            'AllowDesktopConfig': 1,
            'AllowOverlay': 1,
            'openvr': 0,
            'Devkit': 0,
            'DevkitGameID': '',
            'DevkitOverrideAppID': 0,
            'FlatpakAppID': '',
            'tags': {'0': 'StreamDeck', '1': f'/tmp/streamdeck-myapp/{TEST_USER_ID}'},
            'collections': {'0': 'StreamDeck'}
        },
        '1': {
            'AppName': 'myotherapp',
            'Exe': '"/bin/firefox"',
            'StartDir': f'"{TEST_USER_HOME}"',
            'LaunchOptions': f'--profile /tmp/streamdeck-myotherapp/{TEST_USER_ID} https://blog.ccc.de',
            'AllowDesktopConfig': 1,
            'AllowOverlay': 1,
            'openvr': 0,
            'Devkit': 0,
            'DevkitGameID': '',
            'DevkitOverrideAppID': 0,
            'FlatpakAppID': '',
            'tags': {'0': 'StreamDeck', '1': f'/tmp/streamdeck-myotherapp/{TEST_USER_ID}'},
            'collections': {'0': 'StreamDeck'}
        }
    }
}

TEST_APPS = [AppConfig('myapp', 'https://media.ccc.de', f'/tmp/streamdeck-myapp', hide_address_bar=True),
             AppConfig('myotherapp', 'https://blog.ccc.de', f'/tmp/streamdeck-myotherapp', hide_address_bar=True)]


def initialize_test_environment() -> ():

    test_config_dir = TemporaryDirectory("streamdeck")
    ff_config_dir = TemporaryDirectory("firefox")
    steam_config_dir = TemporaryDirectory("steam")
    test_config = TEST_CONFIG.load(json.loads(TEST_CONFIG.to_json()), test_config_dir.name)
    test_config.firefox_config = FirefoxConfig(command=test_config.firefox_config.command,
                                               config_path=ff_config_dir.name)
    test_config.steam_config = SteamConfig(command=["/bin/steam"], config_path=steam_config_dir.name)

    return test_config_dir, ff_config_dir, steam_config_dir, test_config


def setup_steam_shortcuts(user_id: str, steam_config_dir: str, shortcuts_data=None) \
        -> Path:

    if shortcuts_data is None:
        shortcuts_data = TEST_SHORTCUTS_DATA
    (Path(steam_config_dir) / 'userdata' / user_id / 'config').mkdir(exist_ok=True, parents=True)
    shortcuts_path = Path(steam_config_dir) / 'userdata' / user_id / 'config/shortcuts.vdf'
    with shortcuts_path.open('wb') as f:
        vdf.binary_dump(shortcuts_data, f)

    return shortcuts_path
