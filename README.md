# Scaffolder

A command-line tool to generate folder and file structures from YAML templates.

## Features

- 🚀 **Fast**: Uses asynchronous I/O for efficient file operations
- 🛠️ **Simple**: Define your project structure in a simple YAML file
- 🎨 **Visual**: Rich console output with color-coded status messages and tree visualization
- 🔄 **Non-destructive**: Asks for confirmation before overwriting existing files
- 🧩 **Flexible**: Creates files with or without content, nested directories, and more
- 📊 **Preview**: Visualize your project structure before generating it
- 🔧 **Templates**: Built-in templates for common project structures

## Installation

```bash
pip install scfldr
```

Or install from source:

```bash
git clone https://github.com/utkarshg1/scfldr.git
cd scfldr
pip install -e .
```

## Usage

### Creating Your Project Structure

Create a YAML template file to define your desired file structure:

```yaml
# template.yaml
src:
  main.py: |
    def main():
        print("Hello, world!")

    if __name__ == "__main__":
        main()
  utils:
    helpers.py: |
      def add(a, b):
          return a + b
docs:
  README.md: |
    # My Project

    This is a sample project.
tests:
  test_main.py: |
    def test_sample():
        assert True
# Example with append mode
logs:
  app.log: # Standard write mode (overwrites if file exists)
    content: |
      # Log file initialized
      # App started
  error.log: # Append mode (adds content if file exists)
    content: |
      # Error log entry
      # Will be appended if the file exists
    mode: a
```

Then generate your project structure:

```bash
scfldr generate-structure --template template.yaml --output my_project
```

The tool will:

1. Ask for confirmation before overwriting existing files
2. Display a colorful tree visualization of the generated structure
3. Show real-time progress with color-coded status messages

### Creating Example Templates

You can quickly create example template files:

```bash
scfldr create-example --type basic --output my_template.yaml
scfldr create-example --type web --output web_template.yaml
scfldr create-example --type python_package --output pkg_template.yaml
```

You can also print the raw template content to the terminal for easy copying:

```bash
scfldr create-example --type basic --print-raw
```

### Previewing Structure

Preview the structure defined in your template without generating files. This will display a colorful tree visualization of the project structure:

```bash
scfldr show-structure --template template.yaml
```

### Checking Version

You can check the installed version of Scaffolder:

```bash
scfldr --version
```

### Command Line Options

```
Usage: scfldr [COMMAND] [OPTIONS]

Generate folder/file structure from a YAML template.

Commands:
  generate-structure     Generate a project structure from a YAML template
  show-structure         Preview the directory structure from a YAML template
  create-template-file   Create a YAML template file from predefined examples
  create-example         Generate an example YAML template file

Options:
  --help                 Show this message and exit
  --version, -V         Show version and exit

Generate Structure Options:
  --template PATH, -t PATH  Path to the YAML template. [default: template.yaml]
  --output PATH, -o PATH    Output directory root. [default: .]
  --force, -f / --no-force  Overwrite existing output directory if it exists.

Show Structure Options:
  --template PATH, -t PATH  Path to the YAML template. [default: template.yaml]

Create Template File Options:
  TEMPLATE_NAME          Name of the template to create (e.g., 'basic', 'web', 'python_package')
  --output-path PATH     Output path for the YAML template file. [default: template.yaml]
  --print-raw, -p        Print raw template content to terminal for easy copying

Create Example Options:
  --output PATH, -o PATH    Path to save the example template. [default: template.yaml]
  --type TEXT               Type of template to generate (basic, web, python_package). [default: basic]
  --force, -f / --no-force  Overwrite existing file if it exists.
  --print-raw, -p           Print raw template content to terminal for easy copying
```

## YAML Template Format

The YAML template follows a simple structure:

- Keys represent directory or file names
- Generated templates use literal style (`|`) for multiline strings to preserve formatting
- Values represent:
  - For directories: A nested dictionary defining child entities
  - For files:
    - String content (can be multiline using YAML's `|` syntax)
    - OR a dictionary with `content` and optional `mode` keys
      - `mode: a` to append content to an existing file
      - `mode: w` (default) to create or overwrite a file
  - For empty directories: An empty dictionary `{}`

### Examples:

```yaml
# Basic structure
project:
  src:
    main.py: |
      def main():
          print("Hello, world!")
    utils: {} # Empty directory
  README.md: "# Project Title"
```

```yaml
# Structure with append mode
project:
  src:
    main.py: |
      def main():
          print("Hello, world!")
  logs:
    app.log: # Standard write mode (default)
      content: "Log entry"
    error.log: # Append mode
      content: "Error message"
      mode: a # 'a' for append, 'w' for write (default)
```

## Predefined Templates

Scaffolder comes with several predefined templates that you can use to quickly start a project:

### Basic Template

A simple project structure with source files, documentation, and tests.

```bash
scfldr create-template-file basic --output-path basic_template.yaml
```

You can also print the raw template content to the terminal:

```bash
scfldr create-template-file basic --print-raw
```

### Web Template

A Flask web application with static files, templates, and basic setup.

```bash
scfldr create-template-file web --output-path web_template.yaml
```

### Python Package Template

A standard Python package structure with tests, setup.py, and more.

```bash
scfldr create-template-file python_package --output-path package_template.yaml
```

## Development

### Requirements

- Python 3.10+
- Dependencies:
  - typer
  - pyyaml
  - asyncio
  - aiofiles
  - rich

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
