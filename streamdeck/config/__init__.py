import json
from appdirs import user_config_dir

from .Configuration import Configuration
from .AppConfig import AppConfig
from .SteamConfig import SteamConfig


DEFAULT_CONFIG_PATH = user_config_dir('streamdeck')


def load_config_from_file(config_path: str = DEFAULT_CONFIG_PATH) -> Configuration:
    with open(config_path, "r") as f:
        json_config = json.load(f)

    return Configuration.load(json_config, config_path)
