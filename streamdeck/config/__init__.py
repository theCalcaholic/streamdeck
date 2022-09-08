import json
import os

from appdirs import user_config_dir
import os
from os.path import expanduser
from pathlib import Path

from .Configuration import Configuration
from .AppConfig import AppConfig
from .SteamConfig import SteamConfig
from .FirefoxConfig import FirefoxConfig


DEFAULT_CONFIG_PATH = str(Path(user_config_dir('streamdeck')) / 'config.json')


def load_config_from_file(config_path: str = DEFAULT_CONFIG_PATH) -> Configuration:
    with open(config_path, "r") as f:
        json_config = json.load(f)

    return Configuration.load(json_config, config_path)


def load_default_config() -> Configuration:
    return Configuration(FirefoxConfig.autodetect(), SteamConfig.autodetect(), config_path=DEFAULT_CONFIG_PATH)


def load_test_config() -> Configuration:
    return Configuration(
            firefox_profile_prefix='ff-prefix-',
            firefox_config=FirefoxConfig(command=['/bin/firefox'], config_path=expanduser("~/.mozilla/firefox")),
            steam_config=SteamConfig(command=["/bin/steam"], config_path="~/.steam/Steam"),
            config_path="/tmp/streamdeck.config")
