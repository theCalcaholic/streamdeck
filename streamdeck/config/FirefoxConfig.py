import shutil
from dataclasses import dataclass
import subprocess
import os
from os.path import expanduser
from shutil import which
from pathlib import Path


def find_firefox_flatpak() -> (str | None, str | None):
    for location in ('--user', '--system'):
        ff_command = ["flatpak", "run", location, "org.mozilla.firefox"]
        if is_valid_command(ff_command):
            break

        ff_command = None
    return ff_command, f'{expanduser("~")}/.var/app/org.mozilla.firefox/.mozilla/firefox'


def find_firefox_native() -> (str | None, str | None):
    ff_command = which("firefox")
    if ff_command is not None:
        ff_command = [ff_command]
    return ff_command, f'{expanduser("~")}/.mozilla/firefox'


def is_valid_command(cmd: list[str] | None):
    if cmd is None or len(cmd) == 0 \
            or not (Path(cmd[0]).is_file() or shutil.which(cmd[0]))\
            or not os.access(cmd[0], os.X_OK):
        print("invalid")
        return False
    if cmd[0].endswith("flatpak"):
        for expected in ["run", "org.mozilla.firefox"]:
            if expected not in cmd:
                return False
        result = subprocess.run(["info" if arg == "run" else arg for arg in cmd])
        if result.returncode != 0:
            return False
    return True


@dataclass(frozen=True)
class FirefoxConfig:
    command: list[str] | None
    config_path: str | None
    autodetected: bool = False

    @property
    def is_flatpak(self):
        return self.command is not None and self.command[0].endswith('flatpak')

    @classmethod
    def autodetect(cls):
        (command, config_path) = find_firefox_flatpak()
        if command is None:
            (command, config_path) = find_firefox_native()
            if command is None:
                return FirefoxConfig(None, None, False)
        return FirefoxConfig(command, config_path, True)

    @classmethod
    def load(cls, config: dict):
        if "autodetected" in config and config["autodetected"]:
            return FirefoxConfig.autodetect()

        return FirefoxConfig(
            command=config.get('command', None),
            config_path=config.get('config_path', None),
            autodetected=False
        )

