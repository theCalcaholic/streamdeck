from os.path import expanduser
from dataclasses import dataclass
from .util import find_flatpak, find_binary
from abc import ABC
from typing import ClassVar


@dataclass(frozen=True, kw_only=True)
class SystemApplicationConfig(ABC):
    flatpak_id: ClassVar[str]
    binary_name: ClassVar[str]
    config_suffix: ClassVar[str]

    command: list[str] | None
    config_path: str | None
    autodetected: bool = False

    @property
    def is_flatpak(self):
        return self.command is not None and self.command[0].endswith('flatpak')

    @classmethod
    def autodetect(cls):
        (command, config_path) = find_flatpak(cls.flatpak_id)
        if command is None:
            command = find_binary(cls.binary_name)
            if command is None:
                return cls(command=None, config_path=None, autodetected=False)
            else:
                config_path = f"{expanduser('~')}"
        return cls(command=command, config_path=f"{config_path}/{cls.config_suffix}", autodetected=True)

    @classmethod
    def load(cls, config: dict):
        if "autodetected" in config and config["autodetected"]:
            return cls.autodetect()

        return cls(
            command=config.get('command', None),
            config_path=config.get('config_path', None),
            autodetected=False
        )

