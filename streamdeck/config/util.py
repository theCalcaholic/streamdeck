from os.path import expanduser
from shutil import which
from pathlib import Path
import os
import subprocess
from typing import Union



cmd_prefix = [arg for arg in os.environ.get('STREAMDECK_CMD_PREFIX', '').split(' ') if arg is not '']

def find_flatpak(uid: str) -> (Union[list[str], None], Union[str, None]):
    for location in ('--user', '--system'):
        ff_command = ["flatpak", "run", location, uid]
        if is_valid_command(ff_command):
            break

        ff_command = None
    return ff_command, f'{expanduser("~")}/.var/app/{uid}'


def find_binary(name) -> Union[list[str], None]:
    result = subprocess.run(cmd_prefix + ['which', name], capture_output=True)
    cmd = result.stdout.decode('utf-8').strip()
    if result.returncode == 0 and is_valid_command([cmd]):
        return [cmd]
    return None


def is_valid_command(cmd: Union[list[str], None]) -> bool:
    if cmd is None:
        return False
    prefixed_cmd = cmd_prefix + cmd
    exec_path = prefixed_cmd[0] if Path(prefixed_cmd[0]).is_file() else which(prefixed_cmd[0])
    if len(cmd) == 0 or exec_path is None or not os.access(exec_path, os.X_OK):
        return False
    if cmd[0].endswith("flatpak"):
        for expected in ["run"]:
            if expected not in cmd:
                return False
        result = subprocess.run(["info" if arg == "run" else arg for arg in prefixed_cmd])
        if result.returncode != 0:
            return False
    return True
