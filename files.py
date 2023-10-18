"""Classes and functions for working with files"""

import os
import sys
from inspect import ismodule, isclass, isfunction
from importlib import import_module
from pathlib import Path
from settings import CONFIG

sys.path.insert(0, ".")


class DataTypes:
    """Holds various object data"""

    methods: list = None
    functions: list = None
    classes: list = None
    global_variables: list = None
    modules: list = None

    def __init__(self, name: str):
        self.name = name
        self.methods = []
        self.functions = []
        self.classes = []
        self.global_variables = []
        self.modules = []


def get_mod_from_file(filename: str):
    """Import a Python file as a module

    Args:
        filename (str): Path to the Python file to process

    Returns:
        Imported module object
    """

    filename = filename.replace(".py", "").replace("-", "_")
    parts = filename.split(CONFIG.os_sep)

    if len(parts) > 1:
        package = parts[0]
        path = ".".join(parts[1:])
        print(f"Importing module {path} from package {package}")
        import_module(parts[0])
        return import_module(f".{path}", package=package)
    else:
        print(f"Importing: {filename}")
        return import_module(filename)


def is_valid(filename: str):
    """Returns True if filename does not contain excluded text

    Args:
        filename: Name to inspect

    Returns:
        True if the filename passes the test
    """

    if CONFIG.excluded_files:
        for partial in CONFIG.excluded_files:
            if filename.startswith(partial):
                return False  # Not a valid filename
    return True  # A valid filename or no list provided


def find_files(directory: [str, Path]):
    """Find all eligible Python files for inspection, recursively

    Args:
        directory: Starting directory in which to find files

    Returns:
        List of filenames, relative to current working directory
    """

    files = []
    cwd = Path(directory)

    dirs = [x for x in cwd.iterdir() if x.is_dir() and is_valid(x.name)]
    files += [
        x.as_posix()
        for x in cwd.iterdir()
        if x.is_file() and is_valid(x.name) and x.match("*.py")
    ]

    for subdir in dirs:
        files += find_files(cwd.joinpath(subdir.name))

    return files


def find_functions(mod, filter_module: str) -> DataTypes:
    """Find classes, methods, functions within an object

    Args:
        mod: A class object or module to inspect
        filter_module: Name of module to inspect. All others are ignored

    Returns:
        DataTypes instance
    """

    result = DataTypes(mod.__name__)
    print(f"Processing module: {mod.__name__}")

    for item in dir(mod):
        obj = getattr(mod, item)

        # Skip internal use only objects
        if item.startswith("_"):
            continue

        # Check if object is part of the module (not an import)
        if hasattr(obj, "__module__") and obj.__module__ != filter_module:
            continue

        # Categorize the object
        if ismodule(obj):
            print(f"\tModule: {obj.__name__}")
            result.modules.append(obj)
        elif isclass(obj):
            print(f"\tClass: {obj.__name__}")
            result.classes.append(obj)
        elif isfunction(obj):
            print(f"\tFunction: {obj.__name__}")
            result.functions.append(obj)
        else:
            pass  # TODO: global vars

    return result
