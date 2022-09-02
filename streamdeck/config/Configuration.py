from dataclasses import dataclass, field, asdict, InitVar
from shutil import which
import json
from typing import Optional
from os.path import expanduser
from pathlib import Path

from .AppConfig import AppConfig
from .FirefoxConfig import FirefoxConfig

FIREFOX_CONFIG_CANDIDATES_NATIVE = (f"{expanduser('~')}/.var/apps/org.mozilla.firefox/.mozilla/firefox",)
FIREFOX_CONFIG_CANDIDATES_FLATPAK = (f"{expanduser('~')}/.mozilla/firefox",)


@dataclass(init=True)
class Configuration:
    firefox_config: FirefoxConfig
    config_path: InitVar[str]
    firefox_command: Optional[str] = None
    firefox_config_path: Optional[str] = None
    apps: list['AppConfig'] = field(default_factory=list)
    firefox_profile_prefix: str = "streamdeck-"

    @classmethod
    def load(cls, json_config: dict, config_path: str) -> 'Configuration':
        args = {}

        for arg_name in ["firefox_config",
                         "firefox_profile_prefix",
                         "apps"]:
            if arg_name in json_config:
                args[arg_name] = json_config[arg_name]

        if "firefox_config" in args:
            args["firefox_config"] = FirefoxConfig.load(args["firefox_config"])
        else:
            args["firefox_config"] = FirefoxConfig.autodetect()

        if "apps" in args:
            args["apps"] = list(map(lambda cfg: AppConfig.load(cfg), args["apps"]))

        return Configuration(config_path=config_path, **args)

    def __post_init__(self, config_path: str):
        setattr(self, "_config_path", config_path)

    @property
    def config_path(self):
        return getattr(self, "_config_path")

    def to_json(self):
        return json.dumps(asdict(self))

    def write(self, config_path: str):
        with open(config_path, "w") as f:
            json.dump(asdict(self), f)
