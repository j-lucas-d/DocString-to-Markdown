#!/usr/bin/env python3
"""Generates documentation in Markdown format from Docstrings"""

import os
import argparse
import sys
from settings import CONFIG
from files import find_files, find_functions, get_mod_from_file
from formatting import FormattedText


def main():
    """Finds all Python files, retrieves docstrings, and generates Markdown text

    Returns:
        None. Writes documents to disk.
    """

    result = {}
    doc_strings = {}

    # Make directory visible to Python for importing
    sys.path.append(CONFIG.directory)

    # Create destination directory if it doesn't exist
    if not os.path.exists(CONFIG.destination):
        os.makedirs(CONFIG.destination)

    # Find all eligible files
    files = find_files(CONFIG.directory)

    # Create text for the document(s), separated by filename
    for fname in files:
        # Find all classes and functions
        module_name = fname.replace(".py", "")
        mod = get_mod_from_file(fname)
        doc_strings[module_name] = mod.__doc__  # Save file docstring for index document
        func_data = find_functions(mod, module_name)

        # Store module information
        result[module_name] = dict(
            mod=mod, func_data=func_data, formatted=FormattedText(), filename=fname
        )

    # Create document files
    if CONFIG.single_doc_mode:
        with open(os.path.join(CONFIG.destination, CONFIG.single_doc_name), "w") as f:
            FormattedText().format_title()
            for name, data in result.items():
                data["formatted"].format_filename(data["mod"], data["filename"])
                data["formatted"].format_docs(data["func_data"], name)
                f.write(data["formatted"].formatted_text())

            # Write footer
            data = FormattedText()
            data.format_footer()
            f.write(data.formatted_text())

    else:  # Multiple documents
        # Setup index file
        index_data = FormattedText()
        index_data.format_title()

        # Create multiple documents
        for name, data in result.items():
            doc_name = os.path.join(CONFIG.destination, name + ".md")
            with open(doc_name, "w") as f:
                data["formatted"].format_title()
                data["formatted"].format_filename(data["mod"], data["filename"])
                data["formatted"].format_docs(data["func_data"], name)
                data["formatted"].format_footer()
                f.write(data["formatted"].formatted_text())

                # Update index information
                index_data.add_index(name, data["mod"].__doc__)

        # Write index document
        with open(os.path.join(CONFIG.destination, "index.md"), "w") as f:
            index_data.format_footer()
            f.write(index_data.formatted_text())


def parse_args() -> argparse:
    """Creates an argparse instance"""

    parser = argparse.ArgumentParser(description="Docstring to Markdown generator")

    parser.add_argument(
        "-s",
        action="store_true",
        help="Writes the entire document into a single file. Defaults to multiple files",
        required=False,
    )
    parser.add_argument(
        "-m",
        action="store_true",
        help="Default. Writes one document per inspected file",
        required=False,
    )
    parser.add_argument(
        "-sc",
        action="store_true",
        help="Writes function source code to the document",
        required=False,
    )
    parser.add_argument(
        "-nc",
        action="store_true",
        help="Default. Disables writing source code to the document",
        required=False,
    )
    parser.add_argument(
        "-d",
        nargs=1,
        metavar="Directory to store documents in",
        help=(
            "Set directory to write documents to. Creates it if it doesn't exist. "
            "Defaults to current directory"
        ),
        required=False,
    )
    parser.add_argument(
        "-t",
        nargs=1,
        metavar="Title of document",
        help="Usually the same as the project name. Set the title of the document",
        required=False,
    )
    parser.add_argument(
        "-desc",
        nargs=1,
        metavar="Description of the document",
        help=(
            "Set directory to write documents to. Creates it if it doesn't exist. "
            "Defaults to current directory"
        ),
        required=False,
    )
    parser.add_argument(
        "-dd",
        nargs=1,
        metavar="Destination directory",
        help="The directory in which to write the document(s)",
        required=False,
    )
    parser.add_argument(
        "-c",
        nargs=1,
        metavar="Configuration filename",
        help="Defaults to a file created in CWD. Specify the configuration file path",
        required=False,
    )

    return parser.parse_args()


def create_docs(
    title: str = None,
    description: str = None,
    directory: str = None,
    destination: str = None,
    config_file: str = None,
    single_doc_mode: bool = False,
    multiple_doc_mode: bool = False,
    show_source: bool = False,
    hide_source: bool = False,
):
    """Python interface to generate documentation"""

    # Setup configuration, overwrite existing if need be
    if title:
        CONFIG.title = title
    if description:
        CONFIG.description = description
    if directory:
        CONFIG.directory = directory
    if destination:
        CONFIG.destination = destination
    if config_file:
        CONFIG._filename = config_file
    if single_doc_mode:
        CONFIG.single_doc_mode = True
    if multiple_doc_mode:
        CONFIG.single_doc_mode = False
    if show_source:
        CONFIG.show_source = True
    if hide_source:
        CONFIG.show_source = False

    # Check and save new configuration
    CONFIG.is_invalid()
    CONFIG.save_config()

    main()


if __name__ == "__main__":
    args = parse_args()

    # Setup configuration, overwrite existing if need be
    if args.t:
        CONFIG.title = args.t[0]
    if args.desc:
        CONFIG.description = args.desc[0]
    if args.d:
        CONFIG.directory = args.d[0]
    if args.dd:
        CONFIG.destination = args.dd[0]
    if args.c:
        CONFIG._filename = args.c[0]
    if args.s:
        CONFIG.single_doc_mode = True
    if args.m:
        CONFIG.single_doc_mode = False
    if args.sc:
        CONFIG.show_source = True
    if args.nc:
        CONFIG.show_source = False

    # Check and save new configuration
    CONFIG.is_invalid()
    CONFIG.save_config()

    main()
