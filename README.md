# DSM - DocString-to-Markdown

Generates documentation in Markdown format from Docstrings.

## Why another document generator?

I was unsatisfied with the document generators which build from docstrings. I couldn't find one which could easily generate documents in Markdown. So, I made this tool to be exceedingly simple, and to do exactly one thing. And hopefully, do it well.

Markdown was chosen because it's easy to read as text, be read formatted in an IDE, and is the default format for Github readme's. This allows the documents to be easily read and navigated in the IDE or on Github, and removes the need for a separate document source. 

## Is this better than hand-written documents?

That depends. An attentive team with effective processes in place can quickly update manually created documentation in a timely manner. With that you get (likely) better formatting, and extra details which you may not want in Python docstrings.

However, in my experience working on various teams and writing those documents, that equates to extra work. An extra ticket to update the documentation when new functions are added. Extra time that has to be set aside for what is always going to be a lower priority task. And, having to format by hand, is always a pain.

By having an automatically generated document, you remove the cost of manual documentation for the price of that extra information and flexibility. As long as you do the work of having excellent docstrings. Which, we all should anyway.

## Documentation For This Project

You can view the automatically generated documentation for this project as an example [here](docs/index.md).

## Usage

**Note**: This should be run from the **root** of your project, so that the relative paths always work the same way. Absolute paths are not used because if other team members execute this, the path you set will not work for them, due to the path stored in the configuration file.

After the first run, a configuration file is created in the project's root directory. Afterward, you simply need to invoke the program without arguments, and it will use what is saved in the config file. You can update the config file at anytime by including a new setting on the command line or via the Python API.

### Command Line Interface

The CLI provides several arguments to customise the generated documents:
```
-s: Single mode. Creates a single document called API.md. If not specified, one document per inspected file is created, along with an index file.
-d <dir>: The directory in which to look for files to extract docstrings from. Moves recursively through the file system starting here. Defaults to current working directory.
-dd <dir>: The destination directory where the documents should be placed. Defaults to current working directory. If you specify a directory which does not exist, it will be created for you.
```

These are the minimum arguments required to generate documentation. Title and description.
```bash
./create_docs.py -t "Project name" -desc "Description of my project"
```

### Python

The function call is similar to the CLI, where title and description are mandatory, and the defaults are the same.

This is especially useful for when you have a project which is built and packaged for upload to a hosting service, or you can execute it with your test run. You can trust the documentation will always be up-to-date. And, if your docstrings are always proper, you'll know your documentation is as well.

```python
from create_docs import create_docs

create_docs(
    title="Project name",
    description="Description of my project",
    directory=".",
    destination=".",
    config_file=None,
    single_doc_mode=None,
    multiple_doc_mode=None,
    show_source=None,
    hide_source=None,
)
```

## Todo
- Sort functions and classes. Difficult because we store objects, not names
- Find a more elegant solution to displaying docstrings properly with indenting and highlighting
- Add CLI for exclude
- Bug: some directories cause program crash
- Bug: When docs are stored in sub-directory, the link to the Python file doesn't work
- Added the option of specifying the document filename when -s is used for single mode

## Caveats
- Files are imported as modules
- Any code not within a function or `if __name == "__main__"` block will be executed when the file is read. Which may cause problems
- All modules required by the inspected file must be available. So if you are running your project within a specific environment, you must generate the documents from there as well
- Good document formatting depends on good docstring formatting
- Any changes you make to the generated documents will be lost the next time the documents are generated
