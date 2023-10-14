#!/usr/bin/env python3
"""Generates documentation in Markdown format from Docstrings"""

import os
import argparse
from inspect import (
    ismodule,
    isclass,
    isfunction,
    getsource,
    getdoc,
    getargvalues,
    formatargvalues,
    getfullargspec,
)
from importlib import import_module
import sys
from pathlib import Path
from time import strftime

EXCLUDED_FILES = [".", "__", "test_"]
SINGLE_DOC_NAME = "API.md"
NAME = "DocString-to-Markdown"
URL = "https://github.com/j-lucas-d/DocString-to-Markdown"
INCLUDE_SOURCE = False


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
    filename = filename.replace(".py", "").replace(os.sep, ".")
    print(f"Importing: {filename}")
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
    print(f"Processing module: {mod.__name__}")

    for item in dir(mod):
        obj = getattr(mod, item)

        if item.startswith("_"):
            continue

        if hasattr(obj, "__module__") and obj.__module__ != filter_module:
            continue

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


def process_arguments(data: getfullargspec):
    """Creates Markdown for the arguments list

    Args:
        data: Object containing argument data

    Returns:
        Markdown formatted text
    """

    print(data)
    result = ["**Arguments**"]
    if data.args:
        for arg in data.args:
            if arg not in ("self", "cls"):
                result.append(f"- {arg}")
                if data.annotations.get(arg):
                    result[-1] += f" ({data.annotations.get(arg).__name__})"

    if data.annotations.get("return"):
        result.append("\n**Returns**: ")
        result.append(data.annotations["return"].__name__)

    result.append("\n")
    return "\n".join(result)


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
        result.append(f"{func.__doc__}\n")
        result.append(process_arguments(getfullargspec(func)))
        if INCLUDE_SOURCE:
            result.append(f"```python\n{getsource(func)}```\n")
        if not func.__doc__:
            result[-1] = "!!! WARNING: NO DOCSTRING FOUND !!!"
            print(f"Warning: No docstring found for: {func.__name__}!", file=sys.stderr)
        result.append("\n---\n")  # Horizontal rule

    # Classes second
    for cls in data.classes:
        result.append(f"### CLASS: {cls.__name__}\n")
        result.append(f"{cls.__doc__}\n")
        if not cls.__doc__:
            result[-1] = "!!! WARNING: NO DOCSTRING FOUND !!!"
            print(f"Warning: No docstring found for: {cls.__name__}!", file=sys.stderr)
        cls_data = find_functions(cls, filter_module)
        # Recurse into class to find subclasses and methods
        rec_result = format_docs(cls_data, filter_module, _path=_path + cls.__name__)
        if rec_result:
            result.append("\n" + rec_result)
        else:  # Functions put in a rule, this one is needed if a class has no methods
            result.append("\n---\n")  # Horizontal rule

    if result:
        result = "\n".join(result)
    return result


def format_footer():
    """Creates a footer and the end of each document

    Returns:
        Markdown formatted text
    """
    timestamp = strftime("%d %B %Y")
    return f"\n\n*Automatically generated by [{NAME}]({URL}) {timestamp}*\n"


def format_title(title: str, description: str):
    """Creates a Markdown formatted title and description

    Args:
        title: Title of document
        description: Description of document

    Returns:
        Markdown formatted text
    """
    return f"# {title}\n\n{description}\n\n"


def format_filename(mod, path: str):
    """Creates a Markdown formatted module header

    Args:
        mod: Module object
        path: Path to module

    Returns:
        Markdown formatted text
    """
    return f"## FILE: [{mod.__name__}]({path})\n\n{mod.__doc__}\n"


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


def parse_args():
    """Creates an argparse instance"""

    parser = argparse.ArgumentParser(description="Docstring to Markdown generator")

    parser.add_argument(
        "-s",
        action="store_false",
        help="Writes the entire document into a single file. Defaults to multiple files",
    )
    parser.add_argument(
        "-c",
        action="store_true",
        help="Writes function source code to the document",
    )
    parser.add_argument(
        "-d",
        nargs=1,
        default=".",
        metavar="Directory to store documents in",
        help=(
            "Set directory to write documents to. Creates it if it doesn't exist. "
            "Defaults to current directory"
        ),
    )
    parser.add_argument(
        "-t",
        nargs=1,
        metavar="Title of document",
        help="Usually the same as the project name. Set the title of the document",
    )
    parser.add_argument(
        "-desc",
        nargs=1,
        metavar="Description of the document",
        help=(
            "Set directory to write documents to. Creates it if it doesn't exist. "
            "Defaults to current directory"
        ),
    )
    parser.add_argument(
        "-dd",
        nargs=1,
        metavar="Destination directory",
        default=".",
        help="The directory in which to write the document(s)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    return parser.parse_args()


def create_docs(
    title: str,
    description: str,
    directory: str = ".",
    multiple: bool = True,
    destination: str = ".",
    show_source: bool = False,
):
    """Finds all Python files, retrieves docstrings, and generates Markdown text

    Args:
        title: Title of project
        description: Description of project
        directory: Default CWD. Directory to inspect for docstrings
        multiple: Default True. When True, splits documents into multiple files, otherwise
        stores the entire document in a single file
        destination: Defaults current working directory. The directory in which to write
        the document(s)
        show_source: Default False. When True, puts function code into the documents as code blocks

    Returns:
        None. Writes documents to disk.
    """

    result = {}
    doc_strings = {}
    global INCLUDE_SOURCE
    INCLUDE_SOURCE = show_source

    # Make directory visible to Python for importing
    sys.path.append(directory)

    # Create destination directory if it doesn't exist
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Find all eligible files
    files = find_files(directory)

    # Create text for the document(s)
    for fname in files:
        # Find all classes and functions
        module_name = fname.replace(".py", "")
        mod = get_mod_from_file(fname)
        doc_strings[module_name] = mod.__doc__  # Save file docstring for index document
        func_data = find_functions(mod, module_name)

        # Extract and store docstrings
        result[module_name] = []
        result[module_name].append(format_filename(mod, fname))
        result[module_name].append(format_docs(func_data, module_name))

    # Create document files
    if multiple:
        with open(os.path.join(destination, "index.md"), "w") as idx:
            idx.write(format_title(title, description))
            for module_name, text in result.items():
                # Create document
                with open(os.path.join(destination, module_name + ".md"), "w") as f:
                    f.write(format_title(title, description))
                    f.write("\n".join(text))
                    f.write(format_footer())
                # Update index document
                doc = doc_strings[module_name]
                idx.write(f"- [{module_name}.md]({module_name}.md): {doc}\n")
            idx.write(format_footer())

    else:  # Single document
        with open(os.path.join(destination, SINGLE_DOC_NAME), "w") as f:
            f.write(format_title(title, description))
            for text in result.values():
                f.write("\n".join(text))
            f.write(format_footer())


if __name__ == "__main__":
    args = parse_args()
    assert args.t, "Must provide title"
    assert args.desc, "Must provide description"

    create_docs(
        directory=args.d[0],
        title=args.t[0],
        description=args.desc[0],
        multiple=args.s,
        destination=args.dd[0],
        show_source=args.c,
    )
