from os.path import expanduser
from shutil import which
from pathlib import Path
import os
import subprocess


def find_flatpak(uid: str) -> (list[str] | None, str | None):
    for location in ('--user', '--system'):
        ff_command = ["flatpak", "run", location, uid]
        if is_valid_command(ff_command):
            break

        ff_command = None
    return ff_command, f'{expanduser("~")}/.var/app/{uid}'


def find_binary(name) -> list[str] | None:
    ff_command = which(name)
    if ff_command is not None:
        return [ff_command]
    return ff_command


def is_valid_command(cmd: list[str] | None) -> bool:
    if cmd is None or len(cmd) == 0 \
            or not (Path(cmd[0]).is_file() or which(cmd[0])) \
            or not os.access(cmd[0], os.X_OK):
        return False
    if cmd[0].endswith("flatpak"):
        for expected in ["run"]:
            if expected not in cmd:
                return False
        result = subprocess.run(["info" if arg == "run" else arg for arg in cmd])
        if result.returncode != 0:
            return False
    return True
