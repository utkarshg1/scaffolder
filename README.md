# Scaffolder

A command-line tool to generate folder and file structures from YAML templates.

## Features

- 🚀 **Fast**: Uses asynchronous I/O for efficient file operations
- 🛠️ **Simple**: Define your project structure in a simple YAML file
- 🎨 **Visual**: Rich console output with color-coded status messages
- 🔄 **Non-destructive**: Asks for confirmation before overwriting existing files
- 🧩 **Flexible**: Creates files with or without content, nested directories, and more

## Installation

```bash
pip install scaffolder
```

Or install from source:

```bash
git clone https://github.com/yourusername/scaffolder.git
cd scaffolder
pip install -e .
```

## Usage

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
scaffolder --template template.yaml --output my_project
```

### Command Line Options

```
Usage: scaffolder [OPTIONS]

  Generate folder/file structure from a YAML template.

Options:
  --template PATH                 Path to the YAML template.  [required]
  --output PATH                   Output directory root.  [default: ./output]
  --force / --no-force            Overwrite existing output directory if it
                                  exists.
  --help                          Show this message and exit.
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

## Development

### Requirements

- Python 3.7+
- Dependencies:
  - typer
  - pyyaml
  - asyncio
  - aiofiles
  - rich

### Running Tests

```bash
pytest
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
