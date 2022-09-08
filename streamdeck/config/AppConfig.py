import re
from dataclasses import dataclass, field
from .Serializable import Serializable
from .FirefoxConfig import FirefoxConfig
from os.path import expanduser
from pathlib import Path


@dataclass(frozen=True, init=True)
class AppConfig(Serializable):
    name: str
    url: str
    firefox_profile_dir: str
    hide_address_bar: bool = True

    def get_launch_args(self, user: str):
        args = ["--kiosk"] if self.hide_address_bar else []
        firefox_profile = self.get_firefox_profile_path(user)
        try:
            flatpak_config_path = expanduser('~/.var/app/org.mozilla.firefox')
            firefox_profile = str(Path(expanduser('~')) / firefox_profile.relative_to(f"{flatpak_config_path}"))
        except ValueError:
            pass
        return args + ["--profile", str(firefox_profile), self.url]

    @classmethod
    def load(cls, config: dict) -> 'AppConfig':
        return AppConfig(
            name=config["name"],
            url=config["url"],
            firefox_profile_dir=config["firefox_profile_dir"],
            hide_address_bar=config.get("hide_address_bar", True))

    def is_installed_for_user(self, user: str):
        return (Path(self.firefox_profile_dir) / user).is_dir()

    def get_firefox_profile_path(self, user: str):
        return Path(self.firefox_profile_dir) / user

    def to_shortcut(self, firefox: FirefoxConfig, user: str) -> dict:
        return {
            'AppName': self.name,
            'Exe': f'"{firefox.command[0]}"',
            'StartDir': expanduser("~"),
            'LaunchOptions': '"' + "\" \"".join(firefox.command[1:] + self.get_launch_args(user)) + '"',
            'AllowDesktopConfig': 1,
            'AllowOverlay': 1,
            'openvr': 0,
            'Devkit': 0,
            'DevkitGameID': '',
            'DevkitOverrideAppID': 0,
            'FlatpakAppID': '',
            'tags': {'0': 'StreamDeck', '1': str(Path(self.get_firefox_profile_path(user)))},
            'collections': {'0': 'StreamDeck'}
        }
