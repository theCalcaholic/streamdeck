from dataclasses import dataclass, field, asdict, InitVar
from pathlib import Path
import json
from os.path import expanduser
from os import PathLike
from typing import Union

from .AppConfig import AppConfig
from .FirefoxConfig import FirefoxConfig
from .SteamConfig import SteamConfig

FIREFOX_CONFIG_CANDIDATES_NATIVE = (f"{expanduser('~')}/.var/apps/org.mozilla.firefox/.mozilla/firefox",)
FIREFOX_CONFIG_CANDIDATES_FLATPAK = (f"{expanduser('~')}/.mozilla/firefox",)


@dataclass(init=True)
class Configuration:
    firefox_config: FirefoxConfig
    steam_config: SteamConfig
    firefox_config: FirefoxConfig
    config_path: InitVar[str]
    firefox_profile_prefix: str = "streamdeck-"
    apps: list['AppConfig'] = field(default_factory=list)

    @classmethod
    def load(cls, json_config: dict, config_path: str) -> 'Configuration':
        args = {}

        for arg_name in ["firefox_config",
                         "steam_config",
                         "firefox_profile_prefix",
                         "apps"]:
            if arg_name in json_config:
                args[arg_name] = json_config[arg_name]

        if "firefox_config" in args:
            args["firefox_config"] = FirefoxConfig.load(args["firefox_config"])
        else:
            args["firefox_config"] = FirefoxConfig.autodetect()
        if "steam_config" in args:
            args["steam_config"] = SteamConfig.load(args["steam_config"])
        else:
            args["steam_config"] = SteamConfig.autodetect()

        if "apps" in args:
            args["apps"] = [AppConfig.load(app) for app in args["apps"]]

        return Configuration(config_path=config_path, **args)

    def __post_init__(self, config_path: str):
        setattr(self, "_config_path", config_path)

    @property
    def config_path(self) -> str:
        return getattr(self, "_config_path")

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    def dump(self, config_path: Union[str, PathLike[str]]) -> None:
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(asdict(self), f)
