# CC Template

A CLI tool for generating Quarto books optimized for GitHub Pages deployment.

## Features

- **Quick Setup**: Create new Quarto book projects from templates
- **GitHub Pages Ready**: Builds directly to `docs/` directory for easy deployment
- **Simple CLI**: Three main commands - `new`, `config`, and `build`
- **Template-based**: Extensible template system for different book types
- **Config-driven**: YAML configuration file for all template variables
- **Re-processable**: Update config and re-apply to templates anytime
- **Jinja2 Templating**: Flexible template variable replacement system

## Installation

### Prerequisites

- Python 3.7+
- [Quarto](https://quarto.org/docs/get-started/)

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd cc-template

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

## Usage

### Create a new book project

```bash
# Create a new book project
cc-template new my-book

# Specify output directory
cc-template new my-book --output /path/to/projects
```

This creates a new directory with the Quarto book template and a `cc-config.yml` configuration file.

### Build the book

```bash
cc-template build my-book
```

This renders the book to the `docs/` directory, ready for GitHub Pages deployment.

### Customize your book

After creating a project, edit the `cc-config.yml` file to customize your book:

```yaml
# Basic book metadata
title: "My Amazing Book"
author: "Jane Doe"
date: "2025-01-01"

# Additional variables
description: "A comprehensive guide to..."
version: "1.0.0"
publisher: "My Publisher"

# Custom variables for your templates
my_custom_variable: "custom value"
```

### Re-process templates

After editing the config file, apply the changes:

```bash
cc-template config my-book
```

This re-processes all template files with your updated configuration.

#### Template Variables

Templates can use any variables defined in `cc-config.yml`:

- `{{ title }}` - Book title
- `{{ author }}` - Author name  
- `{{ date }}` - Publication date
- `{{ project_name }}` - Project directory name
- Any custom variables you add to the config

#### CLI Options

- `--output, -o`: Output directory for new projects (default: current directory)

## GitHub Pages Deployment

1. Create your book project and build it
2. Commit the `docs/` directory to your repository
3. In your GitHub repository settings, enable Pages and set source to "Deploy from a branch"
4. Select the `main` branch and `/docs` folder
5. Your book will be available at `https://username.github.io/repository-name`

## Template Structure

The default template includes:

- `_quarto.yml` - Quarto configuration
- `index.qmd` - Main page
- `intro.qmd` - Introduction chapter
- `summary.qmd` - Summary chapter
- `references.qmd` - References page
- `references.bib` - Bibliography file

## Development

See [CLAUDE.md](CLAUDE.md) for development setup and guidelines.

## License

MIT License