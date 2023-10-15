"""Class to format docstrings in Markdown"""

from inspect import getsource, getfullargspec
import sys
from time import strftime
import re
from files import find_functions, DataTypes
from settings import CONFIG


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
    def bullet_indent(text: str) -> str:
        """Replace an indent with a bullet"""
        return re.sub(r"^\s+", "- ", text)

    @staticmethod
    def is_sphinx_arg(text: str) -> bool:
        """Returns True if text is a Sphinx style argument"""
        return bool(re.findall(r"^(\s+:)", text))

    @staticmethod
    def is_blank_line(text: str) -> bool:
        """Return True if text is a blank line or whitespace"""
        if re.findall(r"^$", text) or re.findall(r"^\s+$", text):
            return True
        return False


class FormattedText:
    """Class to format docstrings in Markdown"""

    url = "https://github.com/j-lucas-d/DocString-to-Markdown"
    name = "DocString-to-Markdown"

    def __init__(self):
        self.formatted_lines = []

    def _process_arguments(self, data: getfullargspec):
        """Creates Markdown for the arguments list

        Args:
            data: Object containing argument data

        Returns:
            Markdown formatted text
        """

        self.formatted_lines.append("**Arguments**")
        if data.args:
            for arg in data.args:
                if arg not in ("self", "cls"):
                    self.formatted_lines.append(f"- {arg}")
                    if data.annotations.get(arg):
                        self.formatted_lines[
                            -1
                        ] += f" ({data.annotations.get(arg).__name__})"

        self.formatted_lines.append("\n**Returns**: ")
        if data.annotations.get("return"):
            self.formatted_lines.append(data.annotations["return"].__name__)
        else:
            self.formatted_lines.append("- Unknown")

        self.formatted_lines.append("\n")

    def _process_docstring(self, text: str):
        result = []
        indent_args = False  # Determine docstring format type

        for line in text.split("\n"):
            if TextModifier.is_arg_header(line):
                result.append(TextModifier.highlight_arg_header(line))
                indent_args = True
            elif TextModifier.is_return_header(line):
                result.append(TextModifier.highlight_return_header(line))
                indent_args = True
            elif TextModifier.is_indented_arg(line) and indent_args:
                result.append(TextModifier.bullet_indent(line))
            elif TextModifier.is_sphinx_arg(line):
                result.append(TextModifier.bullet_indent(line))
            else:
                if TextModifier.is_blank_line(line):
                    indent_args = False
                result.append(TextModifier.remove_indentation(line))

        print(">>", result)
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
        self.formatted_lines.append(f"{self._process_docstring(docstring)}\n")
        self._process_arguments(arguments)
        self.horizontal_rule()

        if CONFIG.show_source:
            self.formatted_lines.append(f"```python\n{source}```\n")

    def _document_classes(
        self, name: str, docstring: str, arguments: getfullargspec, _path: str = ""
    ):
        if not docstring:
            docstring = "!!! WARNING: NO DOCSTRING FOUND !!!"

        self.formatted_lines.append(f"### CLASS: {name}\n")
        self.formatted_lines.append(f"{self._process_docstring(docstring)}\n")
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
                arguments=getfullargspec(func),
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
                arguments=getfullargspec(cls),
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
        self.formatted_lines.append(
            f"## FILE: [{mod.__name__}]({path})\n\n{mod.__doc__}\n"
        )

    def add_index(self, name: str, docstring: str):
        """Adds a bulleted line to index Markdown files"""
        self.formatted_lines.append(f"- [{name}.md]({name}.md): {docstring}\n")

    def formatted_text(self):
        """Returns collected text as a string"""
        return "\n".join(self.formatted_lines)
