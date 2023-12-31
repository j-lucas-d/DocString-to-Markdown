# DSM - DocString to Markdown

Automatically generated reference documentation.


## FILE: [formatting](../formatting.py)

Class to format docstrings in Markdown

### CLASS: Arguments

Data class to hold argument data

### FUNCTION: Arguments.add_arg

Store an argument name


---

### FUNCTION: Arguments.add_ret

Record if a return statement was found


---

### FUNCTION: Arguments.has_arg

Check if an argument has been recorded


---

### FUNCTION: Arguments.has_ret

Check if a return statement was recorded


---

### CLASS: FormattedText

Class to format docstrings in Markdown

### FUNCTION: FormattedText.add_index

Adds a bulleted line to index Markdown files


---

### FUNCTION: FormattedText.format_docs

Creates formatted Markdown text for the classes and functions
provided

**Args:**
- data: DataTypes instance containing function objects
- filter_module: Name of module to inspect. All others are ignored
- _path: Do not use. Used within the function to track the module path

**Returns:**
- Markdown formatted text



---

### FUNCTION: FormattedText.format_filename

Creates a Markdown formatted module header

**Args:**
- mod: Module object
- path: Path to module

**Returns:**
- Markdown formatted text



---

### FUNCTION: FormattedText.format_footer

Creates a footer and the end of each document

**Returns:**
- Markdown formatted text



---

### FUNCTION: FormattedText.format_title

Creates a Markdown formatted title and description

**Returns:**
- Markdown formatted text



---

### FUNCTION: FormattedText.formatted_text

Returns collected text as a string


---

### FUNCTION: FormattedText.horizontal_rule

Creates a horizontal rule


---

### CLASS: TextModifier

Methods for recognising common docstring patterns and reformatting them

### FUNCTION: TextModifier.bullet_indent

Replace an indent with a bullet


---

### FUNCTION: TextModifier.get_arg_name

Returns the argument name from a docstring


---

### FUNCTION: TextModifier.highlight_arg_header

Adds a bullet to a docstring argument


---

### FUNCTION: TextModifier.highlight_return_header

Bold a return header


---

### FUNCTION: TextModifier.is_arg_header

Return true if text is an indented argument


---

### FUNCTION: TextModifier.is_blank_line

Return True if text is a blank line or whitespace


---

### FUNCTION: TextModifier.is_indented_arg

Return True if text is indented, which may indicate an argument


---

### FUNCTION: TextModifier.is_param_arg

Returns True if text is a colon param argument


---

### FUNCTION: TextModifier.is_return_header

Return True if a return section is detected


---

### FUNCTION: TextModifier.is_sphinx_arg

Returns True if text is a Sphinx style argument


---

### FUNCTION: TextModifier.is_sphinx_return

Returns True if text is a Sphinx style argument


---

### FUNCTION: TextModifier.remove_indentation

Removes any leading whitespace


---



*Automatically generated by [DocString-to-Markdown](https://github.com/j-lucas-d/DocString-to-Markdown) 16 October 2023*
