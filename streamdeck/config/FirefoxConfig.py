from dataclasses import dataclass
from typing import ClassVar
from .SystemApplicationConfig import SystemApplicationConfig


@dataclass(frozen=True, kw_only=True)
class FirefoxConfig(SystemApplicationConfig):
    flatpak_id: ClassVar[str] = "org.mozilla.firefox"
    binary_name: ClassVar[str] = "firefox"
    config_suffix: ClassVar[str] = ".mozilla/firefox"
