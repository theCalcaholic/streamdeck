import re

from streamdeck.config import Configuration, AppConfig, SteamConfig, FirefoxConfig
from pathlib import Path
from typing import Optional
from jinja2 import Template
from streamdeck.steam import Shortcuts
import vdf


def install_userchrome_css(app: AppConfig):
    (Path(app.firefox_profile) / 'chrome').mkdir(parents=True)
    with (Path(__file__).parent / "userChrome.css.jinja2").open("r") as f:
        template = Template(f.read())
    rendered = template.render(hide_adress_bar=app.hide_address_bar)
    with (Path(app.firefox_profile) / 'chrome' / 'userChrome.css').open("w") as f:
        f.write(rendered)


def install_shortcut(steam: SteamConfig, user_id: str, firefox: FirefoxConfig, app: AppConfig):
    shortcuts = Shortcuts.load(steam, user_id)
    shortcuts[app] = app.to_shortcut(firefox)
    shortcuts.dump()


class AppManager:

    def __init__(self, config: Configuration):
        self.config = config

    @property
    def apps(self) -> list[AppConfig]:
        return self.config.apps.copy()

    def profile_exists(self, uid: str):
        return (Path(self.config.firefox_config.config_path) / uid).is_dir()

    def get_unique_profile_uid(self, uid: str, num: Optional[int] = None):
        profile_uid = f"{self.config.firefox_profile_prefix}{uid}{num if num is not None else ''}"
        if self.profile_exists(profile_uid):
            return self.get_unique_profile_uid(uid, 0 if num is None else num+1)
        return profile_uid

    def add_app(self, name: str, url: str, hide_adress_bar: bool = True):
        profile_uid = self.get_unique_profile_uid(name)
        app = AppConfig(name, url, str(Path(self.config.firefox_config.config_path) / profile_uid),
                        hide_address_bar=hide_adress_bar)
        self.config.apps.append(app)
        self.install_app(app)

    def install_app(self, app: AppConfig):
        Path(app.firefox_profile).mkdir(parents=True)
        install_userchrome_css(app)
        for user in self.config.users:
            install_shortcut(self.config.steam_config, user, self.config.firefox_config, app)


