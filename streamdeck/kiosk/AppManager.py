from streamdeck.config import Configuration, AppConfig
from pathlib import Path
from typing import Optional


class AppManager:

    def __init__(self, config: Configuration):
        self.config = config

    @property
    def apps(self) -> list[AppConfig]:
        return self.config.apps.copy()

    def profile_exists(self, uid: str):
        return (Path(self.config.config_path) / uid).is_dir()

    def get_unique_profile_uid(self, uid: str, num: Optional[int] = None):
        profile_uid = f"{self.config.firefox_profile_prefix}{uid}{num if num is not None else ''}"
        if self.profile_exists(profile_uid):
            return self.get_unique_profile_uid(uid, 0 if num is None else num+1)
        return profile_uid

    def add_app(self, name: str, url: str, hide_adress_bar: bool = True):
        profile_uid = self.get_unique_profile_uid(name)

