import vdf
from pathlib import Path
from streamdeck.config import SteamConfig, AppConfig
import shutil
from os import PathLike


class Shortcuts:
    def __init__(self, shortcuts: dict, shortcuts_path: PathLike | None = None):
        self.shortcuts_path = shortcuts_path
        self._shortcuts = shortcuts

    @classmethod
    def shortcut_matches(cls, shortcut: dict, app: AppConfig):
        return app.firefox_profile in shortcut["tags"].values()

    def _find_app_shortcut(self, app: AppConfig):
        try:
            return next(((k, s) for k, s in self._shortcuts["shortcuts"].items()
                         if self.__class__.shortcut_matches(s, app)))
        except StopIteration:
            raise KeyError(app)

    def __getitem__(self, app: AppConfig) -> dict:
        return self._find_app_shortcut(app)[1]

    def __setitem__(self, app: AppConfig, app_shortcut: dict):
        self.update(app, app_shortcut, merge=False)

    def update(self, app: AppConfig, app_shortcut: dict, merge=True):
        try:
            k, old_shortcut = self._find_app_shortcut(app)
            self._shortcuts["shortcuts"][k] = old_shortcut | app_shortcut if merge else app_shortcut
        except KeyError:
            keys = sorted(self._shortcuts["shortcuts"].keys())
            self._shortcuts["shortcuts"][str(int(keys[-1])+1)] = app_shortcut

    def __delitem__(self, app: AppConfig) -> None:
        k, shortcut = self._find_app_shortcut(app)
        del self._shortcuts['shortcuts'][k]

    def all(self) -> list[dict]:
        return list(self._shortcuts["shortcuts"].values())

    @classmethod
    def load(cls, steam: SteamConfig, user_id: str) -> 'Shortcuts':
        shortcuts_path = Path(steam.config_path) / 'userdata' / user_id / 'config' / 'shortcuts.vdf'
        with shortcuts_path.open("rb") as f:
            return Shortcuts(vdf.binary_load(f), shortcuts_path)

    def dump(self, file_path: PathLike | None = None):
        new_values = {
            "shortcuts": {
                str(index): elem for index, elem in enumerate(list(self._shortcuts["shortcuts"].values()))
            }
        }
        file_path = file_path or self.shortcuts_path
        if file_path is None:
            raise ValueError('No file path specified!')
        if Path(file_path).exists():
            shutil.copyfile(file_path, Path(file_path).with_stem('shortcuts_backup'))
        with open(file_path, "wb") as f:
            vdf.binary_dump(new_values, f)

    def __enter__(self):
        if self.shortcuts_path is None:
            raise ValueError("No shortcuts path is configured!. Shortcuts.shortcuts_path is required for using it as "
                             "contextmanage (i.e. in with... statement)!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.dump(self.shortcuts_path)
        else:
            raise exc_val


