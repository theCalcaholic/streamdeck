from dataclasses import dataclass, field
from .Serializable import Serializable
from .FirefoxConfig import FirefoxConfig
from os.path import expanduser
from hashlib import sha256


@dataclass(frozen=True, init=True)
class AppConfig(Serializable):
    name: str
    url: str
    firefox_profile: str
    hide_address_bar: bool = True

    @property
    def launch_args(self):
        args = ["--kiosk"] if self.hide_address_bar else []
        return args + ["--profile", self.firefox_profile, self.url]

    @classmethod
    def load(cls, config: dict) -> 'AppConfig':
        return AppConfig(
            name=config["name"],
            url=config["url"],
            firefox_profile=config["firefox_profile"],
            hide_address_bar=config.get("hide_address_bar", True))

    def to_shortcut(self, firefox: FirefoxConfig) -> dict:
        return {
            'AppName': self.name,
            'Exe': f'"{firefox.command[0]}"',
            'StartDir': expanduser("~"),
            'LaunchOptions': '"' + "\" \"".join(firefox.command[1:] + self.launch_args) + '"',
            'AllowDesktopConfig': 1,
            'AllowOverlay': 1,
            'openvr': 0,
            'Devkit': 0,
            'DevkitGameID': '',
            'DevkitOverrideAppID': 0,
            'FlatpakAppID': '',
            'tags': {'0': 'StreamDeck', '1': self.firefox_profile},
            'collections': {'0': 'StreamDeck'}
        }
