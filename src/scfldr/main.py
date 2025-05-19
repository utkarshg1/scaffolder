import asyncio
import yaml
import typer
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
import aiofiles
from typing import Dict, Any
import sys
import importlib.metadata

# Initialize console for rich output
console = Console()

# Define the available template types based on the files in the templates folder
EXAMPLE_TEMPLATE_TYPES = ["basic", "web", "python_package"]


def get_literal_style_dumper():
    """
    Returns a YAML dumper configured for human-readable output.

    This dumper will format multiline strings using literal style (|)
    to preserve formatting and make YAML templates more readable.

    Returns:
        A configured YAML dumper class
    """

    class LiteralStyleDumper(yaml.SafeDumper):
        pass

    # Represent multiline strings with literal style (|) to preserve formatting
    def represent_str_literal(dumper, data):
        if "\n" in data:
            # Use literal style for multiline strings
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    LiteralStyleDumper.add_representer(str, represent_str_literal)
    return LiteralStyleDumper


def load_template_from_file(template_name: str) -> Dict[str, Any]:
    """
    Load a YAML template from the templates folder.

    Args:
        template_name: Name of the template (e.g., 'basic', 'web', 'python_package')

    Returns:
        Dictionary containing the parsed YAML structure

    Raises:
        FileNotFoundError: If the template file doesn't exist
        yaml.YAMLError: If the YAML format is invalid
    """
    template_path = Path("src/scfldr/templates") / f"{template_name}.yaml"

    if not template_path.exists():
        console.print(
            f"[bold red]Error:[/] Template '{template_name}' not found in templates folder."
        )
        sys.exit(1)

    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = yaml.safe_load(file)
            if not isinstance(template, dict):
                raise ValueError("Template must be a dictionary/object")
            return template
    except yaml.YAMLError as e:
        console.print(
            f"[bold red]Error:[/] Invalid YAML format in {template_path}: {e}"
        )
        sys.exit(1)
    except Exception as e:
        console.print(
            f"[bold red]Error:[/] Failed to load template from {template_path}: {e}"
        )
        sys.exit(1)


# Initialize Typer app
app = typer.Typer(
    help="Generate folder/file structure from a YAML template. "
    "Files can be created in write mode (default) or append mode."
)


def version_callback(value: bool):
    """
    Display the version of the CLI tool and exit.

    Args:
        value: Boolean flag indicating if version should be displayed
    """
    if value:
        try:
            version = importlib.metadata.version("scfldr")
            console.print(f"scfldr version: [bold green]{version}[/]")
            raise typer.Exit()
        except importlib.metadata.PackageNotFoundError:
            console.print("[bold yellow]Warning:[/] Version information not available")
            raise typer.Exit(1)


# Add version option to the app
app = typer.Typer(
    help="Generate folder/file structure from a YAML template. "
    "Files can be created in write mode (default) or append mode."
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        help="Show version and exit.",
    ),
):
    """
    Main callback for the application.
    """
    pass


def load_template(path: Path) -> Dict[str, Any]:
    """
    Load YAML template from a file.

    Args:
        path: Path to the YAML template file

    Returns:
        Dictionary containing the parsed YAML structure

    Raises:
        FileNotFoundError: If the template file doesn't exist
        yaml.YAMLError: If the YAML format is invalid
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            template = yaml.safe_load(file)
            if not isinstance(template, dict):
                raise ValueError("Template must be a dictionary/object")
            return template
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Template file not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[bold red]Error:[/] Invalid YAML format: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to load template: {e}")
        sys.exit(1)


async def create_entity(base: Path, name: str, content: Any) -> None:
    """
    Recursively create a directory and file structure.

    Args:
        base: Base directory path
        name: Name of the entity to create
        content: Content definition (dict for directories, string for files)
            - For files, content can be a string or a dictionary with 'content' and 'mode' keys
            - 'mode' can be 'w' (write/overwrite) or 'a' (append)
    """
    target = base / name

    try:
        if isinstance(content, dict) and ("content" in content and "mode" in content):
            # Handle file with append/write mode specification
            parent = target.parent
            parent.mkdir(parents=True, exist_ok=True)

            file_content = content.get("content", "")
            file_mode = content.get("mode", "w")  # Default to write mode

            if file_mode not in ("w", "a"):
                console.print(
                    f"[bold yellow]Warning:[/] Invalid mode '{file_mode}' for {target}. Using 'w' (write) mode."
                )
                file_mode = "w"

            async with aiofiles.open(target, file_mode, encoding="utf-8") as file:
                await file.write(str(file_content))

            mode_desc = "Appended to" if file_mode == "a" else "Created"
            console.print(f"[green]{mode_desc} file:[/] {target}")

        elif isinstance(content, dict) and not (
            "content" in content and "mode" in content
        ):
            # Handle directory with children
            target.mkdir(parents=True, exist_ok=True)
            tasks = [
                create_entity(target, child_name, child_content)
                for child_name, child_content in content.items()
            ]
            await asyncio.gather(*tasks)

        elif target.suffix or isinstance(content, str):
            # Handle file with content (traditional way)
            parent = target.parent
            parent.mkdir(parents=True, exist_ok=True)

            text = content or ""
            async with aiofiles.open(target, "w", encoding="utf-8") as file:
                await file.write(str(text))
            console.print(f"[green]Created file:[/] {target}")

        else:
            # Handle empty directory
            target.mkdir(parents=True, exist_ok=True)
            console.print(f"[blue]Created directory:[/] {target}")

    except PermissionError:
        console.print(f"[bold red]Error:[/] Permission denied when creating {target}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to create {target}: {e}")


async def generate(template_path: Path, output: Path) -> None:
    """
    Main routine to load the template and generate the structure.

    Args:
        template_path: Path to the YAML template file
        output: Output directory where the structure will be generated
    """
    console.print(f"[bold]Loading template:[/] {template_path}")
    template = load_template(template_path)

    console.print(f"[bold]Generating structure in:[/] {output.resolve()}")

    # Kick off tasks for top-level entries
    tasks = []
    for name, content in template.items():
        tasks.append(create_entity(output, name, content))

    await asyncio.gather(*tasks)


def display_tree(path: Path, parent: Tree | None = None) -> Tree:
    """
    Generate a rich Tree representation of the directory structure.

    Args:
        path: Path to the root directory to display
        parent: Parent tree node (used for recursion)

    Returns:
        Tree: A Rich Tree object representing the directory structure
    """
    if parent is None:
        parent = Tree(f"[bold blue]{path.name}[/]", guide_style="bold bright_blue")

    # Sort paths - directories first, then files
    paths = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

    for item in paths:
        if item.is_dir():
            # Add directory with a bold blue style
            branch = parent.add(f"[bold blue]{item.name}[/]")
            display_tree(item, branch)
        else:
            # Add file with a green style
            parent.add(f"[green]{item.name}[/]")

    return parent


@app.command()
def generate_structure(
    template: Path = typer.Option(
        Path("template.yaml"), "--template", "-t", help="Path to the YAML template."
    ),
    output: Path = typer.Option(
        Path("."), "--output", "-o", help="Output directory root."
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing output directory if it exists."
    ),
):
    """
    CLI entrypoint: kicks off the async generator.

    Args:
        template: Path to the YAML template file
        output: Output directory where the structure will be generated
        force: Whether to overwrite the output directory if it exists
    """  # Check if output directory exists and is not empty
    if output.exists() and any(output.iterdir()) and not force:
        # Check if the output directory is default (.) and only contains YAML files
        is_default_with_yaml_only = False
        if output == Path("."):
            yaml_files_only = all(
                f.is_file() and f.suffix.lower() in [".yaml", ".yml"]
                for f in output.iterdir()
                if f.is_file()
            )
            is_default_with_yaml_only = yaml_files_only

        if is_default_with_yaml_only:
            console.print(
                f"[bold blue]Info:[/] Proceeding with default directory containing only YAML files."
            )
        else:
            console.print(
                f"[bold yellow]Warning:[/] Output directory {output} already exists and is not empty."
            )
            if not typer.confirm("Continue and potentially overwrite existing files?"):
                console.print("Operation cancelled.")
                return

    # Create output directory if it doesn't exist
    output.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(generate(template, output))
        console.print(
            f"[bold green]Success![/] Structure generated at: {output.resolve()}"
        )

        # Display the directory tree structure
        console.print("\n[bold]Directory Structure:[/]")
        tree = display_tree(output)
        console.print(tree)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return 1


def preview_tree(
    path: Path, template: Dict[str, Any], parent: Tree | None = None
) -> Tree:
    """
    Recursively preview the directory structure as a tree from a template.

    Args:
        path: Current directory path
        template: Current level template content
        parent: Parent tree node

    Returns:
        The tree node representing the current directory level
    """
    if parent is None:
        parent = Tree(path.name, guide_style="bold bright_blue")

    for name, content in template.items():
        if isinstance(content, dict):
            # Recursive case: directory
            node = parent.add(f"[blue]{name}[/]", guide_style="bold blue")
            preview_tree(path / name, content, node)
        else:
            # Base case: file
            parent.add(f"[green]{name}[/]")

    return parent


@app.command()
def show_structure(
    template: Path = typer.Option(
        Path("template.yaml"), "--template", "-t", help="Path to the YAML template."
    ),
):
    """
    CLI entrypoint: displays the directory structure from the YAML template.

    Args:
        template: Path to the YAML template file
    """
    console.print(f"[bold]Loading template:[/] {template}")
    template_content = load_template(template)

    console.print("[bold]Directory structure:[/]")
    tree = preview_tree(Path("."), template_content)
    console.print(tree)


@app.command()
def create_template_file(
    template_name: str = typer.Argument(
        ...,
        help="Name of the template to create (e.g., 'basic', 'web', 'python_package')",
    ),
    output_path: Path = typer.Option(
        Path("template.yaml"),
        "--output-path",
        "-o",
        help="Output path for the YAML template file.",
    ),
    print_raw: bool = typer.Option(
        False,
        "--print-raw",
        "-p",
        help="Print raw template content to terminal for easy copying",
    ),
):
    """
    Create a YAML template file from predefined examples stored in the templates folder.

    Args:
        template_name: Name of the template to create
        output_path: Output path for the YAML template file
        print_raw: Whether to print the raw template content to terminal
    """
    template_name = template_name.lower()

    # Load the template from the templates folder
    template_content = load_template_from_file(template_name)

    # Write to the output file with improved formatting
    with open(output_path, "w", encoding="utf-8") as file:
        yaml.dump(
            template_content,
            file,
            Dumper=get_literal_style_dumper(),
            sort_keys=False,
            default_flow_style=False,
            indent=2,
            width=80,
            allow_unicode=True,
        )

    console.print(f"[bold green]Template file created:[/] {output_path}")

    # Print raw template for copying if requested
    if print_raw:
        console.print("\n[bold]Raw template content for copying:[/]")
        with open(output_path, "r", encoding="utf-8") as file:
            raw_content = file.read()
        console.print(raw_content)


@app.command()
def create_example(
    output: Path = typer.Option(
        Path("template.yaml"),
        "--output",
        "-o",
        help="Path to save the example template.",
    ),
    template_type: str = typer.Option(
        "basic",
        "--type",
        "-t",
        help="Type of template to generate (basic, web, python_package).",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing file if it exists."
    ),
    print_raw: bool = typer.Option(
        False,
        "--print-raw",
        "-p",
        help="Print raw template content to terminal for easy copying",
    ),
):
    """
    Generate an example YAML template file.

    Args:
        output: Path where to save the example template
        template_type: Type of template to generate (basic, web, python_package)
        force: Whether to overwrite the output file if it exists
        print_raw: Whether to print the raw template content to terminal
    """
    # Check if output file exists
    if output.exists() and not force:
        console.print(f"[bold yellow]Warning:[/] Output file {output} already exists.")
        if not typer.confirm("Overwrite existing file?"):
            console.print("Operation cancelled.")
            return  # Check if selected template type exists
    if template_type not in EXAMPLE_TEMPLATE_TYPES:
        console.print(
            f"[bold red]Error:[/] Unknown template type: {template_type}. "
            f"Available types: {', '.join(EXAMPLE_TEMPLATE_TYPES)}"
        )
        return 1

    # Get the template content by loading it from file
    template_content = load_template_from_file(template_type)

    try:
        with open(output, "w", encoding="utf-8") as file:
            yaml.dump(
                template_content,
                file,
                Dumper=get_literal_style_dumper(),
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=80,
                allow_unicode=True,
            )

        console.print(
            f"[bold green]Success![/] Example template generated at: {output.resolve()}"
        )

        # Preview the template
        console.print("\n[bold]Template structure preview:[/]")
        tree = preview_tree(Path("."), template_content)
        console.print(tree)

        # Print raw template for copying if requested
        if print_raw:
            console.print("\n[bold]Raw template content for copying:[/]")
            with open(output, "r", encoding="utf-8") as file:
                raw_content = file.read()
            console.print(raw_content)

        console.print(f"\nUse it with: [bold]scfldr generate-structure[/]")

    except PermissionError:
        console.print(f"[bold red]Error:[/] Permission denied when creating {output}")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to create example template: {e}")
        return 1


if __name__ == "__main__":
    app()
