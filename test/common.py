import json
from tempfile import TemporaryDirectory

from streamdeck.config import Configuration
from streamdeck.config.FirefoxConfig import FirefoxConfig
from streamdeck.config.SteamConfig import SteamConfig


TEST_CONFIG = Configuration(config_path="/tmp", apps=[], firefox_profile_prefix='ff-prefix-',
                            steam_config=SteamConfig(command=['/bin/firefox'],
                                                     config_path='/home/streamdeck/.local/share/Steam'),
                            firefox_config=FirefoxConfig(command=['/bin/firefox'],
                                                         config_path='/home/streamdeck/.mozilla/firefox'))

TEST_USER = 'streamdeck'
TEST_USER_HOME = f'/home/{TEST_USER}'


def initialize_test_environment() -> ():

    test_config_dir = TemporaryDirectory("streamdeck")
    ff_config_dir = TemporaryDirectory("firefox")
    steam_config_dir = TemporaryDirectory("steam")
    test_config = TEST_CONFIG.load(json.loads(TEST_CONFIG.to_json()), test_config_dir.name)
    test_config.firefox_config = FirefoxConfig(command=test_config.firefox_config.command,
                                               config_path=ff_config_dir.name)
    test_config.steam_config = SteamConfig(command=["/bin/steam"], config_path=steam_config_dir.name)

    return test_config_dir, ff_config_dir, steam_config_dir, test_config
