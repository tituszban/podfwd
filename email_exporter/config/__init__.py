import json
import os
import re


class Config:
    def __init__(self):
        self._data = {}

    def _validate_flat_dict(self, d):
        accepted_types = [str, float, int, bool]
        for key, item in d.items():
            assert type(item) in accepted_types, f"Invalid key: {key}; only {accepted_types} allowed"

    def add_json(self, path):
        with open(path) as f:
            d = json.load(f)
        self._validate_flat_dict(d)
        self._data.update(d)
        return self

    def add_env_variables(self, prefix):
        prefix = prefix.upper()
        d = {re.sub(f"^{prefix}", "", key): item
             for key, item in os.environ.items()
             if key.upper().startswith(prefix)}

        self._data.update(d)
        return self

    def add_dictionary(self, d):
        self._validate_flat_dict(d)
        self._data.update(d)
        return self

    def print(self):
        print('\n'.join((f"{key}: {value}"
                         for key, value in self.app.config.items())))
        return self

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def get_bool(self, key, default=False):
        value = self._data.get(key, default)
        if type(value) is bool:
            return value
        return value == "true"
