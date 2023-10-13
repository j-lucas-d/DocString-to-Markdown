# DocString-to-Markdown

Generates documentation in Markdown format from Docstrings

## Usage

### Command Line Interface

The CLI provides several arguments to customise the generated documents:
```
-s: Single mode. Creates a single document called API.md. If not specified, one document per inspected file is created, along with an index file.
-d <dir>: The directory in which to look for files to extract docstrings from. Moves recursively through the file system starting here. Defaults to current working directory.
-dd <dir>: The destination directory where the documents should be placed. Defaults to current working directory. If you specify a directory which does not exist, it will be created for you.
```

These are the minimum arguments required. Title and description.
```bash
./create_docs.py -t "Project name" -desc "Description of my project"
```



### Python
The function call is similar to the CLI, where title and description are mandatory, and the defaults are the same.
```python
from docstring_to_markdown import create_docs

create_docs(
    title="Project name",
    description="Description of my project",
    directory=".",
    multiple=True,
    destination=".",
)
```

## Todo
- Sort functions and classes. Difficult because we store objects, not names
- Add full module path to document filenames. Currently, there's a risk of a name collision

## Caveats
- Files are imported as modules
- Any code not within a function or `if __name == "__main__"` block will be executed when the file is read. Which may cause problems
- All modules required by the inspected file must be available. So if you are running your project within a specific environment, you must generate the documents from there as well
- Good document formatting depends on good docstring formatting
- Any changes you make to the generated documents will be lost the next time the documents are generated
