import asyncio
import yaml
import typer
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
import aiofiles
from typing import Dict, Any, Optional
import sys

# Initialize console for rich output
console = Console()

# Initialize Typer app
app = typer.Typer(help="Generate folder/file structure from a YAML template.")


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
    """
    target = base / name

    try:
        if isinstance(content, dict):
            # Handle directory with children
            target.mkdir(parents=True, exist_ok=True)
            tasks = [
                create_entity(target, child_name, child_content)
                for child_name, child_content in content.items()
            ]
            await asyncio.gather(*tasks)

        elif target.suffix or isinstance(content, str):
            # Handle file with content
            parent = target.parent
            parent.mkdir(parents=True, exist_ok=True)
            text = content or ""
            async with aiofiles.open(target, "w", encoding="utf-8") as file:
                await file.write(text)
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


def display_tree(path: Path, parent: Tree = None) -> Tree:
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
        Path("template.yaml"), help="Path to the YAML template."
    ),
    output: Path = typer.Option(Path("./output"), help="Output directory root."),
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
    """
    # Check if output directory exists and is not empty
    if output.exists() and any(output.iterdir()) and not force:
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


def preview_tree(path: Path, template: Dict[str, Any], parent: Tree = None) -> Tree:
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
    template: Path = typer.Option(..., help="Path to the YAML template."),
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


if __name__ == "__main__":
    app()
