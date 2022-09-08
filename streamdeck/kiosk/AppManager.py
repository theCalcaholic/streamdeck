import re
import shutil
import traceback

from streamdeck.config import Configuration, AppConfig, SteamConfig, FirefoxConfig
from pathlib import Path
from typing import Optional, Iterable
from jinja2 import Template
from streamdeck.steam import Shortcuts
import json


def install_userchrome_css(profile_path: Path, hide_address_bar=True):
    try:
        (profile_path / 'chrome').mkdir(parents=True)
    except FileExistsError:
        pass
    with (Path(__file__).parent / "userChrome.css.jinja2").open("r") as f:
        template = Template(f.read())
    rendered = template.render(hide_adress_bar=hide_address_bar)
    with (profile_path / 'chrome' / 'userChrome.css').open("w") as f:
        f.write(rendered)


class AppManager:

    def __init__(self, config: Configuration):
        self.config = config

    @property
    def apps(self) -> list[AppConfig]:
        return json.loads(json.dumps(self.config.apps))

    def get_unique_profile_uid(self, uid: str, num: Optional[int] = None):
        profile_uid = f"{self.config.firefox_profile_prefix}{uid}{num if num is not None else ''}"
        if (Path(self.config.firefox_config.config_path) / profile_uid).exists():
            return self.get_unique_profile_uid(uid, 0 if num is None else num+1)
        return profile_uid

    def add_app(self, name: str, url: str, hide_adress_bar: bool = True):
        profile_uid = self.get_unique_profile_uid(re.sub(r'[^A-Z0-9a-z._]', '-', name))
        app = AppConfig(name, url, str(Path(self.config.firefox_config.config_path) / profile_uid),
                        hide_address_bar=hide_adress_bar)
        print(f"add_app({app})")
        self.config.apps.append(app)

    def remove_app(self, app: AppConfig):
        print(f"remove_app({app})")
        err_prefix = f"WARN: An error occurred while removing app {app.name}"
        for user in self.config.steam_config.users:
            if app.is_installed_for_user(user):
                self.uninstall_app(app, user)
        try:
            shutil.rmtree(app.firefox_profile_dir)
        except FileNotFoundError as e:
            print(f"{err_prefix}: {e}")
        try:
            self.config.apps.remove(app)
        except ValueError as e:
            print(f"{err_prefix}: {e} ")

    def uninstall_app(self, app: AppConfig, user: str, keep_data=False):
        print(f"uninstall_app({app}, {user}, {keep_data})")
        err_prefix = f"WARN: An error occurred while uninstalling app {app.name} for user {user}"

        with Shortcuts.load(self.config.steam_config, user) as shortcuts:
            try:
                del shortcuts[app]
            except KeyError as e:
                print(shortcuts._shortcuts)
                print(f"{err_prefix}: {e} ")
                traceback.print_exc()

        if not keep_data:
            try:
                shutil.rmtree(app.get_firefox_profile_path(user))
            except FileNotFoundError as e:
                print(f"{err_prefix}: {e}")

    def install_app(self, app: AppConfig, user: str):
        print(f"install_app({app}, {user})")
        app.get_firefox_profile_path(user).mkdir(parents=True, exist_ok=True)
        install_userchrome_css(app.get_firefox_profile_path(user), app.hide_address_bar)
        with Shortcuts.load(self.config.steam_config, user) as shortcuts:
            shortcuts[app] = app.to_shortcut(self.config.firefox_config, user)

    def update_app(self, app_old: AppConfig, app_new: AppConfig):
        print(f"update_app({app_old}, {app_new})")
        index = self.config.apps.index(app_old)
        self.config.apps[index] = app_new

        keep_data = app_old.firefox_profile_dir == app_new.firefox_profile_dir
        for user in self.config.steam_config.users:
            if app_old.is_installed_for_user(user):
                self.uninstall_app(app_old, user, keep_data)
                self.install_app(app_new, user)
