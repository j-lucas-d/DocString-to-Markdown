"""Configuration for documented project"""

import json
import os
from inspect import ismethod
import sys


class Settings:
    """Stores all user-defined settings"""

    # Default settings
    _filename: str = ".dsm.cfg"
    directory: str = "."  # Where Python files are read from
    destination: str = "."  # Where documents are written
    excluded_files: list = [".", "__", "test_"]
    single_doc_mode: bool = True
    single_doc_name: str = "API.md"
    show_source: bool = False
    title: str = None
    description: str = None

    def __init__(self):
        self.read_config()

    def read_config(self):
        """Read settings file from disk into this class"""
        print("Reading configuration file")

        if os.path.exists(self._filename):
            with open(self._filename) as f:
                config = json.load(f)
                if config:
                    # Populate internal attributes with the read configuration values
                    for key, value in config.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                        else:
                            print(
                                f"Warning: Ignoring unknown configuration key found: {key}",
                                file=sys.stderr,
                            )

    def save_config(self):
        """Write settings to disk"""
        print(f"Saving configuration file to {self._filename}")
        config = {}

        for key in [x for x in dir(self) if not x.startswith("_")]:
            if not ismethod(getattr(self, key)):
                config[key] = getattr(self, key)

        with open(self._filename, "w") as f:
            json.dump(config, f)

    def is_invalid(self):
        """Checks for any unset settings"""
        for key in [x for x in dir(self) if not x.startswith("_")]:
            if not ismethod(getattr(self, key)):
                assert getattr(self, key) is not None, f"Error: {key} must be defined"


CONFIG = Settings()
