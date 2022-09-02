from dataclasses import dataclass
from .Serializable import Serializable


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
