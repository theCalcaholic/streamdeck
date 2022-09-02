from dataclasses import dataclass
from typing import ClassVar
from .SystemApplicationConfig import SystemApplicationConfig
from pathlib import Path
import vdf


@dataclass(frozen=True, kw_only=True)
class SteamConfig(SystemApplicationConfig):
    flatpak_id: ClassVar[str] = "com.valvesoftware.Steam"
    binary_name: ClassVar[str] = "steam"
    config_suffix: ClassVar[str] = ".local/share/Steam"

    @property
    def library_paths(self) -> list[Path]:
        lib_config_file = Path(self.config_path) / 'steamapps' / 'libraryfolders.vdf'
        if not lib_config_file.exists():
            return [lib_config_file.parent]
        with lib_config_file.open("r") as f:
            return [Path(line.split('"')[3]) for line in f.readlines() if '"path"' in line]

    @property
    def users(self) -> list[str]:
        dirs = (Path(self.config_path) / 'userdata').glob("[0-9]*")
        return [d.name for d in dirs if d.is_dir() and len(d.name) > 3]

    def get_user_name(self, user_id: str):
        with (Path(self.config_path) / 'userdata' / user_id / 'config' / 'localconfig.vdf').open("r") as f:
            localconfig = vdf.load(f)
        return localconfig["UserLocalConfigStore"]["friends"][user_id]["name"]

