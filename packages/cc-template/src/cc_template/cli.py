"""CLI interface for cc-template."""

import click
import shutil
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from jinja2 import Environment


@click.group()
@click.version_option()
def main():
    """CC Template - CLI tool for Quarto-based book generation."""
    pass


@main.command()
@click.argument("name")
@click.option("--output", "-o", default=".", help="Output directory")
def new(name, output):
    """Create a new Quarto book project."""
    output_path = Path(output) / name
    template_path = Path(__file__).parent.parent.parent / "templates" / "quarto-book"

    click.echo(f"Creating new Quarto book project: {name}")
    click.echo(f"Output directory: {output_path}")

    if output_path.exists():
        click.echo(f"Error: Directory {output_path} already exists")
        return

    # Copy template files first
    _copy_template_files(template_path, output_path)

    # Process config file and apply template variables
    _process_config_and_templates(output_path, name)

    click.echo(f"✓ Project created successfully at {output_path}")
    click.echo(f"✓ Edit {output_path}/cc-config.yml to customize your book settings")


def _copy_template_files(template_path, output_path):
    """Copy all template files without processing."""
    shutil.copytree(template_path, output_path)

    # Create a .templates directory to store original templates for re-processing
    templates_backup = output_path / ".templates"
    templates_backup.mkdir(exist_ok=True)

    # Copy each file individually to avoid gitignore issues
    for item in template_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(template_path)
            target_file = templates_backup / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)


def _process_config_and_templates(project_path, project_name):
    """Process the config file and apply variables to templates."""
    config_file = project_path / "cc-config.yml"

    # Load and process config file
    if config_file.exists():
        config_content = config_file.read_text()

        # First pass: process config file itself with basic variables
        env = Environment()
        config_template = env.from_string(config_content)
        processed_config = config_template.render(
            project_name=project_name, current_date=datetime.now().strftime("%Y-%m-%d")
        )
        config_file.write_text(processed_config)

        # Load the processed config
        config_vars = yaml.safe_load(processed_config)

        # Add built-in variables
        template_vars = {
            "project_name": project_name,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            **config_vars,
        }

        # Second pass: process all template files with config variables
        _apply_template_variables(project_path, template_vars)


def _apply_template_variables(project_path, template_vars):
    """Apply template variables to all template files in the project."""
    templates_backup = project_path / ".templates"

    if not templates_backup.exists():
        click.echo("Warning: No .templates backup found, cannot re-process")
        return

    # Process from original templates in .templates directory
    for item in templates_backup.rglob("*"):
        if item.is_file() and item.name != "cc-config.yml":
            # Calculate target file path
            rel_path = item.relative_to(templates_backup)
            target_file = project_path / rel_path

            # Process template files
            if item.suffix in [".yml", ".yaml", ".qmd", ".md"]:
                content = item.read_text()
                # Only process if file contains Jinja2 variables
                if "{{" in content and "}}" in content:
                    env = Environment()
                    template = env.from_string(content)
                    rendered_content = template.render(**template_vars)
                    target_file.write_text(rendered_content)
                    click.echo(f"  Processed: {rel_path}")
                else:
                    # Copy template files without variables as-is
                    target_file.write_text(content)
            else:
                # For non-template files, just copy as-is
                shutil.copy2(item, target_file)


@main.command()
@click.argument("project_path", type=click.Path(exists=True))
def config(project_path):
    """Re-process templates after config changes."""
    project_path = Path(project_path)
    config_file = project_path / "cc-config.yml"

    if not config_file.exists():
        click.echo(f"Error: No cc-config.yml found in {project_path}")
        return

    # Extract project name from path
    project_name = project_path.name

    click.echo(f"Re-processing templates in: {project_path}")
    _process_config_and_templates(project_path, project_name)
    click.echo("✓ Templates updated with current config settings")


@main.command()
@click.argument("project_path", type=click.Path(exists=True))
def build(project_path):
    """Build a Quarto book project."""
    project_path = Path(project_path)
    docs_path = Path("docs")

    click.echo(f"Building Quarto book at: {project_path}")

    # Ensure docs directory exists
    docs_path.mkdir(exist_ok=True)

    # Run quarto render command
    try:
        subprocess.run(
            [
                "quarto",
                "render",
                str(project_path),
                "--output-dir",
                str(docs_path.absolute()),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        click.echo(f"✓ Book built successfully in {docs_path}")
        click.echo("Ready for GitHub Pages deployment!")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error building book: {e}")
        if e.stdout:
            click.echo(f"stdout: {e.stdout}")
        if e.stderr:
            click.echo(f"stderr: {e.stderr}")
    except FileNotFoundError:
        click.echo("Error: Quarto not found. Please install Quarto first.")


@main.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--topic", help="Book topic/description for outline generation")
@click.option("--provider", help="AI provider (openai/anthropic)")
def outline(project_path, topic, provider):
    """Generate chapter outline from topic using AI."""
    from .ai_client import create_ai_client
    from .prompt_processor import PromptProcessor

    project_path = Path(project_path)

    click.echo(f"Generating outline for project: {project_path}")

    try:
        # Initialize prompt processor
        processor = PromptProcessor(project_path)

        # Update config with topic if provided
        if topic:
            # Load current config
            config_file = project_path / "cc-config.yml"
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)

                # Update topic and save
                config["topic"] = topic
                with open(config_file, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)

                click.echo(f"Updated topic in config: {topic}")

        # Load and process outline prompt
        click.echo("Loading outline prompt...")
        prompt_context = {"topic": topic} if topic else {}
        prompt = processor.load_prompt("outline", prompt_context)

        # Initialize AI client
        click.echo(f"Initializing AI client (provider: {provider or 'auto-detect'})...")
        ai_client = create_ai_client(provider)

        # Generate outline
        click.echo("Generating outline with AI...")
        outline_content = ai_client.generate_content(prompt, max_tokens=4000)

        # Clean up the response to ensure it's valid YAML
        if "```yaml" in outline_content:
            # Extract YAML from code block
            start_idx = outline_content.find("```yaml") + 7
            end_idx = outline_content.find("```", start_idx)
            if end_idx != -1:
                outline_content = outline_content[start_idx:end_idx].strip()
        elif "```" in outline_content:
            # Extract from generic code block
            start_idx = outline_content.find("```") + 3
            end_idx = outline_content.find("```", start_idx)
            if end_idx != -1:
                outline_content = outline_content[start_idx:end_idx].strip()

        # Save outline
        outline_file = processor.save_outline(outline_content)

        click.echo(f"✓ Outline generated and saved to: {outline_file}")
        click.echo("✓ Edit outline.yml to customize chapters before generating content")
        click.echo(
            f"✓ Next: Run 'cc-template generate {project_path.name}' to create chapters"
        )

    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
    except ValueError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
