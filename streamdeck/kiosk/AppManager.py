from streamdeck.config import Configuration, AppConfig
from pathlib import Path
from typing import Optional
from jinja2 import Template


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

    def install_userchrome_css(self, app_id):
        (Path(self.config.apps[app_id].firefox_profile) / 'chrome').mkdir(parents=True)
        with (Path(__file__).parent / "userChrome.css.jinja2").open("r") as f:
            template = Template(f.read())
        rendered = template.render(hide_adress_bar=self.config.apps[app_id].hide_address_bar)
        with (Path(self.config.apps[app_id].firefox_profile) / 'chrome' / 'userChrome.css').open("w") as f:
            f.write(rendered)

    def install_app(self, app_id):
        Path(self.config.apps[app_id].firefox_profile).mkdir(parents=True)
        self.install_userchrome_css(app_id)

    def add_app(self, name: str, url: str, hide_adress_bar: bool = True):
        profile_uid = self.get_unique_profile_uid(name)
        self.config.apps.append(AppConfig(name, url, str(Path(self.config.firefox_config.config_path) / profile_uid)))
        self.install_app(len(self.config.apps) - 1)



