from dataclasses import fields
from typing import Protocol


class IsDataclass(Protocol):
    _FIELDS: dict


class Cloneable:
    def clone(self: IsDataclass):
        for field in fields(self):
            pass

