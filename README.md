# Scaffolder

A command-line tool to generate folder and file structures from YAML templates.

## Features

- 🚀 **Fast**: Uses asynchronous I/O for efficient file operations
- 🛠️ **Simple**: Define your project structure in a simple YAML file
- 🎨 **Visual**: Rich console output with color-coded status messages
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
git clone https://github.com/yourusername/scfldr.git
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
  README.md: "# My Project\n\nThis is a sample project."
tests:
  test_main.py: |
    def test_sample():
        assert True
```

Then generate your project structure:

```bash
scfldr generate-structure --template template.yaml --output my_project
```

### Creating Example Templates

You can quickly create example template files:

```bash
scfldr create-example --type basic --output my_template.yaml
scfldr create-example --type web --output web_template.yaml
scfldr create-example --type python_package --output pkg_template.yaml
```

### Previewing Structure

Preview the structure defined in your template without generating files:

```bash
scfldr show-structure --template template.yaml
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

Generate Structure Options:
  --template PATH        Path to the YAML template. [default: template.yaml]
  --output PATH          Output directory root. [default: .]
  --force / --no-force   Overwrite existing output directory if it exists.

Show Structure Options:
  --template PATH        Path to the YAML template. [default: template.yaml]

Create Template File Options:
  TEMPLATE_NAME          Name of the template to create (e.g., 'basic', 'web', 'python_package')
  --output-path PATH     Output path for the YAML template file. [default: template.yaml]

Create Example Options:
  --output PATH          Path to save the example template. [default: template.yaml]
  --type TEXT            Type of template to generate (basic, web, python_package). [default: basic]
  --force / --no-force   Overwrite existing file if it exists.
```

## YAML Template Format

The YAML template follows a simple structure:

- Keys represent directory or file names
- Values represent:
  - For directories: A nested dictionary defining child entities
  - For files: String content (can be multiline using YAML's `|` syntax)
  - For empty directories: An empty dictionary `{}`

### Example:

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

## Predefined Templates

Scaffolder comes with several predefined templates that you can use to quickly start a project:

### Basic Template

A simple project structure with source files, documentation, and tests.

```bash
scfldr create-template-file basic --output-path basic_template.yaml
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

- Python 3.7+
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
