from dataclasses import dataclass
from .Serializable import Serializable


@dataclass(frozen=True, init=True)
class AppConfig(Serializable):
    name: str
    url: str
    firefox_profile: str

    @classmethod
    def load(cls, config: dict) -> 'AppConfig':
        return AppConfig(
            name=config["name"],
            url=config["url"],
            firefox_profile=config["firefoxProfile"])
