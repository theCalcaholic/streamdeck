from dataclasses import asdict
import json
from .DataclassEncoder import DataclassEncoder


class Serializable:
    def to_json(self):
        return json.dumps(self)

    def write(self, config_path: str):
        with open(config_path, "w") as f:
            json.dump(self, f)


