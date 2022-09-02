from dataclasses import dataclass
from typing import ClassVar
from .SystemApplicationConfig import SystemApplicationConfig


@dataclass(frozen=True, kw_only=True)
class SteamConfig(SystemApplicationConfig):
    flatpak_id: ClassVar[str] = "com.valvesoftware.Steam"
    binary_name: ClassVar[str] = "steam"
    config_suffix: ClassVar[str] = ".local/share/Steam"
