#!/usr/bin/env python3
"""Generates documentation in Markdown format from Docstrings"""

import argparse
from inspect import ismodule, isclass, isfunction, ismethod
from importlib import import_module
import sys
from pathlib import Path

EXCLUDED_FILES = [".", "__", "test_"]


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
    """Import a Python file

    Args:
        filename (str): Path to the Python file to process

    Returns:
        Imported module object
    """
    filename = filename.replace(".py", "").replace("/", ".")
    return import_module(filename)


def find_functions(mod, filter_module: str) -> DataTypes:
    """Find classes, methods, functions within an object

    Args:
        mod: A class object or module to inspect
        filter_module: Name of module to inspect. All others are ignored

    Returns:
        DataTypes instance
    """

    result = DataTypes(mod.__name__)

    for item in dir(mod):
        obj = getattr(mod, item)

        if item.startswith("_"):
            continue

        if hasattr(obj, "__module__") and obj.__module__ != filter_module:
            continue

        if ismodule(obj):
            result.modules.append(obj)
        elif isclass(obj):
            result.classes.append(obj)
        elif isfunction(obj):
            print(">>>>>>>is func", obj.__name__, obj.__module__)
            result.functions.append(obj)
        else:
            pass  # TODO: global vars

    return result


def format_docs(data: DataTypes, filter_module: str, _path: str = ""):
    """Creates formatted Markdown text for the classes and functions
    provided

        Args:
            data: DataTypes instance containing function objects
            filter_module: Name of module to inspect. All others are ignored
            _path: Do not use. Used within the function to track the module path

        Returns:
            Markdown formatted text
    """

    result = []
    if _path:
        _path += "."

    # Functions first
    for func in data.functions:
        result.append(f"### FUNCTION: {_path}{func.__name__}\n")
        result.append(func.__doc__)
        result.append("\n---\n")  # Horizontal rule
        if not func.__doc__:
            print(f"Warning: No docstring found for: {func.__name__}!", file=sys.stderr)

    # Classes second
    for cls in data.classes:
        result.append(f"### CLASS: {cls.__name__}\n")
        result.append(cls.__doc__)
        if not cls.__doc__:
            print(f"Warning: No docstring found for: {cls.__name__}!", file=sys.stderr)
        cls_data = find_functions(cls, filter_module)
        # Recurse into class to find subclasses and methods
        format_docs(cls_data, filter_module, _path=_path + cls.__name__)

    return "\n".join(result)


def format_title(title: str, description: str):
    """Creates a Markdown formatted title and description

    Args:
        title: Title of document
        description: Description of document

    Returns:
        Markdown formatted text
    """
    return f"# {title}\n{description}\n"


def format_filename(name: str, path: str):
    """Creates a Markdown formatted module header

    Args:
        name: Name of module
        path: Path to module

    Returns:
        Markdown formatted text
    """
    return f"## FILE: [{name}]({path})\n"  # TODO: add file docstring


def is_valid(filename: str):
    """Returns True if filename does not contain excluded text

    Args:
        filename: Name to inspect

    Returns:
        True/False
    """
    if EXCLUDED_FILES:
        for partial in EXCLUDED_FILES:
            if filename.startswith(partial):
                return False  # Not a valid filename
    return True  # A valid filename or no list provided


def find_files(directory: str):
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
        files += find_files(subdir.name)

    return files


def main(directory: str, title: str, description: str):
    """Finds all Python files, retrieves docstrings, and generates Markdown text

    Args:
        directory: Directory to inspect for docstrings
        title: Title of project
        description: Description of project
    """

    result = []
    files = find_files(directory)

    result.append(format_title(title, description))

    for fname in files:
        filter_module = fname.replace(".py", "")
        mod = get_mod_from_file(fname)
        func_data = find_functions(mod, filter_module)
        result.append(format_filename(mod.__name__, fname))
        result.append(format_docs(func_data, filter_module))

    print("\n".join(result))


if __name__ == "__main__":
    main(".", "Example Repo", "An excellent project!")
# TODO: should I purhapse use a :::placeholder::: tag to inject the descriptions?
# TODO: Should the doc files be separate? Might make it easier to read
