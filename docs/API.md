# DocString to Markdown

API reference

## FILE: [create_docs](create_docs.py)

Generates documentation in Markdown format from Docstrings

### FUNCTION: create_docs

Finds all Python files, retrieves docstrings, and generates Markdown text

    Args:
        title: Title of project
        description: Description of project
        directory: Default CWD. Directory to inspect for docstrings
        multiple: Default True. When True, splits documents into multiple files, otherwise
        stores the entire document in a single file
        destination: Defaults current working directory. The directory in which to write
        the document(s)

    Returns:
        None. Writes documents to disk.
    

---

### FUNCTION: find_files

Find all eligible Python files for inspection, recursively

    Args:
        directory: Starting directory in which to find files

    Returns:
        List of filenames, relative to current working directory
    

---

### FUNCTION: find_functions

Find classes, methods, functions within an object

    Args:
        mod: A class object or module to inspect
        filter_module: Name of module to inspect. All others are ignored

    Returns:
        DataTypes instance
    

---

### FUNCTION: format_docs

Creates formatted Markdown text for the classes and functions
    provided

        Args:
            data: DataTypes instance containing function objects
            filter_module: Name of module to inspect. All others are ignored
            _path: Do not use. Used within the function to track the module path

        Returns:
            Markdown formatted text
    

---

### FUNCTION: format_filename

Creates a Markdown formatted module header

    Args:
        mod: Module object
        path: Path to module

    Returns:
        Markdown formatted text
    

---

### FUNCTION: format_title

Creates a Markdown formatted title and description

    Args:
        title: Title of document
        description: Description of document

    Returns:
        Markdown formatted text
    

---

### FUNCTION: get_mod_from_file

Import a Python file

    Args:
        filename (str): Path to the Python file to process

    Returns:
        Imported module object
    

---

### FUNCTION: is_valid

Returns True if filename does not contain excluded text

    Args:
        filename: Name to inspect

    Returns:
        True/False
    

---

### FUNCTION: parse_args

Creates an argparse instance

---

### CLASS: DataTypes

Holds various object data