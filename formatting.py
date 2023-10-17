"""Class to format docstrings in Markdown"""

from dataclasses import dataclass
from inspect import getsource, getfullargspec
import sys
from time import strftime
import re
import os
from files import find_functions, DataTypes
from settings import CONFIG


def get_arg_info(func) -> getfullargspec:
    """Wrapper for getfullargspec to protect against retrieving arg data from a built in
    class or function, which always results in an exception
    """
    try:
        return getfullargspec(func)
    except Exception:
        print(f"Warning: Could not retrieve getfullargspec for {func.__name__}")
    return None


class TextModifier:
    """Methods for recognising common docstring patterns and reformatting them"""

    @staticmethod
    def remove_indentation(text: str) -> str:
        """Removes any leading whitespace"""
        return re.sub(r"^\s+", "", text, re.MULTILINE)

    @staticmethod
    def is_arg_header(text: str) -> bool:
        """Return true if text is an indented argument"""
        return bool(re.findall(r"^\s+(Args:?)$", text))

    @staticmethod
    def highlight_arg_header(text: str) -> str:
        """Adds a bullet to a docstring argument"""
        return re.sub(r"\s+(Args:?)$", "**Args:**", text)

    @staticmethod
    def is_return_header(text: str) -> bool:
        """Return True if a return section is detected"""
        return bool(re.findall(r"^\s+(Returns?:?)$", text))

    @staticmethod
    def highlight_return_header(text: str) -> str:
        """Bold a return header"""
        return re.sub(r"\s+(Returns?:?)$", "**Returns:**", text)

    @staticmethod
    def is_indented_arg(text: str) -> bool:
        """Return True if text is indented, which may indicate an argument"""
        return bool(re.findall(r"^(\s+:?[\d\w])", text))

    @staticmethod
    def get_arg_name(text: str) -> str:
        """Returns the argument name from a docstring"""
        patterns = [r"^\s+:param\s+(.*?):\s+.*", r"^\s+(.*?)\s+:\s+.*"]
        for pat in patterns:
            result = re.findall(pat, text)
            if result:
                return result[0]

    @staticmethod
    def bullet_indent(text: str) -> str:
        """Replace an indent with a bullet"""
        return re.sub(r"^\s+", "- ", text)

    @staticmethod
    def is_sphinx_arg(text: str) -> bool:
        """Returns True if text is a Sphinx style argument"""
        return bool(re.findall(r"^(\s+:param\s+.*?:)", text))

    @staticmethod
    def is_sphinx_return(text: str) -> bool:
        """Returns True if text is a Sphinx style argument"""
        return bool(re.findall(r"^(\s+:return:)", text))

    @staticmethod
    def is_blank_line(text: str) -> bool:
        """Return True if text is a blank line or whitespace"""
        if re.findall(r"^$", text) or re.findall(r"^\s+$", text):
            return True
        return False

    @staticmethod
    def is_param_arg(text: str) -> bool:
        """Returns True if text is a colon param argument"""
        return bool(re.findall(r":param\s+(.*?):\s+(.*)", text))


class Arguments:
    """Data class to hold argument data"""

    def __init__(self):
        self.arg_list = []
        self.ret = False

    def add_arg(self, name: str):
        """Store an argument name"""
        self.arg_list.append(name)

    def add_ret(self):
        """Record if a return statement was found"""
        self.ret = True

    def has_arg(self, name: str):
        """Check if an argument has been recorded"""
        return bool(name in self.arg_list)

    def has_ret(self):
        """Check if a return statement was recorded"""
        return self.ret


class FormattedText:
    """Class to format docstrings in Markdown"""

    url = "https://github.com/j-lucas-d/DocString-to-Markdown"
    name = "DocString-to-Markdown"

    def __init__(self):
        self.formatted_lines = []

    @staticmethod
    def _process_arguments(
        func_name: str, inspected_args: getfullargspec, doc_args: Arguments
    ) -> None:
        """Compare docstring arguments with inspected arguments

        Args:
            inspected_args: Object containing argument data from the inspect module
            doc_args: Object containing argument data from the docstring
        """

        for arg_name in inspected_args.args:
            if arg_name not in ("self", "cls") and not doc_args.has_arg(arg_name):
                print(
                    f"WARNING: '{func_name}' missing function argument: {arg_name}",
                    file=sys.stderr,
                )

    def _process_docstring(self, func_name: str, text: str, arg_data: getfullargspec):
        result = []
        indent_args = False  # Determine docstring format type
        indent_ret = False
        doc_args = Arguments()

        for line in text.split("\n"):
            if TextModifier.is_arg_header(line):
                result.append(TextModifier.highlight_arg_header(line))
                indent_args = True
                indent_ret = False
            elif TextModifier.is_return_header(line):
                result.append(TextModifier.highlight_return_header(line))
                indent_args = False
                indent_ret = True
            elif TextModifier.is_indented_arg(line) and indent_args:
                result.append(TextModifier.bullet_indent(line))
                arg_name = TextModifier.get_arg_name(line)
                doc_args.add_arg(arg_name)  # Store for comparison
            elif TextModifier.is_indented_arg(line) and indent_ret:
                result.append(TextModifier.bullet_indent(line))
                doc_args.add_ret()  # Store for comparison
            elif TextModifier.is_sphinx_arg(line):
                result.append(TextModifier.bullet_indent(line))
                arg_name = TextModifier.get_arg_name(line)
                doc_args.add_arg(arg_name)  # Store for comparison
            elif TextModifier.is_sphinx_return(line):
                result.append(TextModifier.bullet_indent(line))
                doc_args.add_ret()  # Store for comparison
            else:
                if TextModifier.is_blank_line(line):
                    indent_args = False
                    indent_ret = False
                result.append(TextModifier.remove_indentation(line))

        if arg_data:
            self._process_arguments(func_name, arg_data, doc_args)

        return "\n".join(result)

    def _document_functions(
        self,
        name: str,
        docstring: str,
        arguments: getfullargspec,
        source: str,
        _path: str = "",
    ):
        if not docstring:
            docstring = "!!! WARNING: NO DOCSTRING FOUND !!!"

        self.formatted_lines.append(f"### FUNCTION: {_path}{name}\n")
        self.formatted_lines.append(
            f"{self._process_docstring(name, docstring, arguments)}\n"
        )
        self.horizontal_rule()

        if CONFIG.show_source:
            self.formatted_lines.append(f"```python\n{source}```\n")

    def _document_classes(
        self, name: str, docstring: str, arguments: getfullargspec, _path: str = ""
    ):
        if not docstring:
            docstring = "!!! WARNING: NO DOCSTRING FOUND !!!"

        self.formatted_lines.append(f"### CLASS: {name}\n")
        self.formatted_lines.append(
            f"{self._process_docstring(name, docstring,arguments)}\n"
        )
        # TODO: Add arguments?

    def format_docs(self, data: DataTypes, filter_module: str, _path: str = ""):
        """Creates formatted Markdown text for the classes and functions
        provided

            Args:
                data: DataTypes instance containing function objects
                filter_module: Name of module to inspect. All others are ignored
                _path: Do not use. Used within the function to track the module path

            Returns:
                Markdown formatted text
        """

        if _path:
            _path += "."

        # Functions first
        for func in data.functions:
            self._document_functions(
                name=func.__name__,
                docstring=func.__doc__,
                arguments=get_arg_info(func),
                source=getsource(func),
                _path=_path,
            )
            if not func.__doc__:
                print(
                    f"Warning: No docstring found for: {func.__name__}!",
                    file=sys.stderr,
                )

        # Classes second
        for cls in data.classes:
            self._document_classes(
                name=cls.__name__,
                docstring=cls.__doc__,
                arguments=get_arg_info(cls),
                _path=_path,
            )
            if not cls.__doc__:
                print(
                    f"Warning: No docstring found for: {cls.__name__}!",
                    file=sys.stderr,
                )

            # Recurse into class to find subclasses and methods
            cls_data = find_functions(cls, filter_module)
            size = len(self.formatted_lines)
            self.format_docs(cls_data, filter_module, _path=_path + cls.__name__)
            if len(self.formatted_lines) == size:
                # Only add a rule if the class had no methods
                self.horizontal_rule()

    def horizontal_rule(self):
        """Creates a horizontal rule"""
        self.formatted_lines.append("\n---\n")

    def format_footer(self):
        """Creates a footer and the end of each document

        Returns:
            Markdown formatted text
        """
        timestamp = strftime("%d %B %Y")
        self.formatted_lines.append(
            f"\n\n*Automatically generated by [{self.name}]({self.url}) {timestamp}*\n"
        )

    def format_title(self):
        """Creates a Markdown formatted title and description

        Returns:
            Markdown formatted text
        """
        self.formatted_lines.append(f"# {CONFIG.title}\n\n{CONFIG.description}\n\n")

    def format_filename(self, mod, path: str):
        """Creates a Markdown formatted module header

        Args:
            mod: Module object
            path: Path to module

        Returns:
            Markdown formatted text
        """
        directory = os.path.relpath(
            os.path.abspath(CONFIG.directory), os.path.abspath(CONFIG.destination)
        )
        self.formatted_lines.append(
            f"## FILE: [{mod.__name__}]({directory}{CONFIG.os_sep}{path})\n\n{mod.__doc__}\n"
        )

    def add_index(self, name: str, docstring: str):
        """Adds a bulleted line to index Markdown files"""
        self.formatted_lines.append(f"- [{name}.md]({name}.md): {docstring}\n")

    def formatted_text(self):
        """Returns collected text as a string"""
        return "\n".join(self.formatted_lines)
