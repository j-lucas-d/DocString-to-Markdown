# DocString-to-Markdown

Generates documentation in Markdown format from Docstrings

## Caveats
- Files are imported as modules
- Any code not within a function or `if __name == "__main__"` block will be executed
- All modules required by the inspected file must be available
