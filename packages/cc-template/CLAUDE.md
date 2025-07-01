# Claude Development Guide

This file contains instructions for Claude Code when working on this project.

## Project Overview

CC Template is a CLI tool for generating AI-powered books using Quarto, optimized for GitHub Pages deployment and publishing platforms like Amazon KDP. The tool creates book projects from templates with AI-generated content, customizable metadata, and builds them to the `docs/` directory for easy deployment.

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Project Structure
- `src/cc_template/` - Main package code
- `src/cc_template/cli.py` - CLI interface using Click
- `templates/` - Book templates with prompts
- `templates/quarto-book/` - Default Quarto book template
- `prompts/` - Shared prompt library (optional)
- `docs/` - Build output directory (ignored in git, created during build)

### Key Commands for Development

#### Testing the CLI
```bash
# Activate virtual environment first
source venv/bin/activate

# Test creating a new book project
cc-template new test-book

# Test generating outline from topic (requires AI API key)
export OPENAI_API_KEY="your-openai-key"  # or ANTHROPIC_API_KEY
cc-template outline test-book --topic "AI in healthcare"

# Edit outline.yml manually, then generate chapters
cc-template generate test-book

# Test building a book
cc-template build test-book

# Clean up test files
rm -rf test-book docs/
```

#### Testing
```bash
# Install dev dependencies (includes pytest)
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=cc_template

# Run specific test file
pytest tests/test_cli.py

# Run tests in verbose mode
pytest -v
```

#### Git Workflow
```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "feat: description of changes"

# Check status
git status
```

## Code Guidelines

### CLI Implementation
- Uses Click framework for command-line interface
- Main commands: `new` (create project), `outline` (generate chapter structure), `generate` (create content), `config` (re-process templates), and `build` (render book)
- All builds output to `docs/` directory for GitHub Pages compatibility
- Pipeline design: new → outline → generate → build

### Book Generation Workflow
1. **Project Creation**: `cc-template new my-book --template non-fiction`
2. **Outline Generation**: `cc-template outline my-book --topic "your topic"`
3. **Manual Editing**: Edit `outline.yml` to refine chapters
4. **Content Generation**: `cc-template generate my-book`
5. **Building**: `cc-template build my-book --format all`

### Template System
- Templates stored in `templates/` directory with prompt subdirectories
- Uses `cc-config.yml` file for all template variables
- `outline.yml` file stores chapter structure (generated, then user-editable)
- Hybrid prompt system: template defaults + project overrides + chapter context
- Uses Jinja2-style placeholders for variables defined in config files
- Preserves Quarto-specific syntax like `{#refs}` divs

### Prompt Management
```
templates/non-fiction-book/
├── _quarto.yml
├── prompts/
│   ├── outline-prompt.txt      # Generate chapter structure
│   ├── chapter-prompt.txt      # Generate chapter content
│   └── intro-prompt.txt        # Specialized prompts
├── chapters/
└── _resources/
```

#### Prompt Processing Order
1. Load base prompt from template
2. Apply Jinja2 template variables (from cc-config.yml)
3. Apply project-level prompt overrides (if specified in config)
4. Merge chapter-specific context
5. Send final prompt to LLM

### File Structure Conventions
```
my-book/
├── cc-config.yml           # Basic metadata and config
├── outline.yml            # Generated, then user-editable chapter structure
├── chapters/              # AI-generated content
│   ├── 01-intro.qmd
│   ├── 02-science.qmd
│   └── ...
├── _generated/            # AI generation metadata and logs
├── .templates/            # Template backup for re-processing
└── _quarto.yml            # Quarto configuration
```

### Build Process
- Uses `quarto render` command to build books
- Supports multiple formats: HTML (for GitHub Pages), PDF (for print), EPUB (for e-readers)
- Configures output directory to `docs/`
- Includes KDP-ready formatting for Amazon publishing

### Configuration Files

#### cc-config.yml Format
```yaml
title: "Book Title"
subtitle: "Optional subtitle"
author: "Author Name"
topic: "Brief book description"
writing_style: "technical but accessible"

# Optional prompt overrides
prompts:
  outline: "path/to/custom-outline-prompt.txt"
  chapter: "path/to/custom-chapter-prompt.txt"

# Publishing metadata
publishing:
  isbn: ""
  categories: ["Technology", "Health"]
  price: 24.99
```

#### outline.yml Format (Generated, then editable)
```yaml
book:
  title: "{{title}}"
  description: "{{topic}}"
  target_length: 50000  # words
  
chapters:
  - id: "intro"
    title: "The Eye as a Window"
    description: "Introduction to retinal imaging potential"
    target_words: 3000
    status: "pending"  # pending|generated|edited
    prompt_context:
      focus: "accessibility for wellness practitioners"
      tone: "engaging but authoritative"
```

## Common Development Tasks

### Adding New Template
1. Create new directory in `templates/`
2. Add `prompts/` subdirectory with prompt files
3. Create template structure with Jinja2 variables
4. Update CLI to support new template type (if needed)

### Adding New Commands
```python
@cli.command()
@click.argument('project_name')
@click.option('--topic', help='Book topic/description')
def outline(project_name, topic):
    """Generate chapter outline from topic using AI"""
    # Load outline prompt from template
    # Process with LLM
    # Write outline.yml
    pass
```

### Testing AI Integration
1. Create test project with outline
2. Test prompt loading and processing
3. Verify outline.yml generation
4. Test chapter content generation
5. Check that generated content integrates properly with Quarto

### Working with Prompts
- Template prompts use Jinja2 variables from cc-config.yml
- Project-level prompt overrides in cc-config.yml prompts section
- Chapter-specific context in outline.yml prompt_context
- Test prompts with different topics and writing styles
- Version control prompt changes for reproducibility

## Dependencies

- Click: CLI framework
- PyYAML: YAML configuration handling  
- Jinja2: Template processing and prompt rendering
- OpenAI/Anthropic: AI content generation APIs
- Quarto: External dependency for rendering (must be installed separately)

## AI Integration Details

### Setup and Configuration

#### API Keys
Set one of the following environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

The system will auto-detect which provider to use based on available API keys.

#### Supported Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 models (Sonnet, Haiku, Opus)

### Content Generation Pipeline
1. **Outline Generation**: Topic → AI → structured chapter outline
2. **Content Generation**: Chapter outline + context → AI → full chapter content
3. **Quality Control**: Validate generated content format and length
4. **Integration**: Insert generated content into Quarto project structure

### Commands

#### Generate Outline
```bash
# Generate outline from topic
cc-template outline my-book --topic "Introduction to Machine Learning"

# Use specific AI provider
cc-template outline my-book --topic "AI Ethics" --provider openai
```

#### Generate Content (Coming Soon)
```bash
# Generate all chapters from outline
cc-template generate my-book

# Generate specific chapter
cc-template generate my-book --chapter intro
```

### Prompt System

#### Default Prompts
- Located in `templates/quarto-book/prompts/`
- `outline-prompt.txt` - Chapter structure generation
- `chapter-prompt.txt` - Individual chapter content

#### Custom Prompts
Override prompts in `cc-config.yml`:
```yaml
prompts:
  outline: "path/to/custom-outline-prompt.txt"
  chapter: "path/to/custom-chapter-prompt.txt"
```

#### Prompt Variables
All prompts have access to config variables:
- `{{title}}` - Book title
- `{{topic}}` - Book topic/description
- `{{writing_style}}` - Target writing style
- `{{author}}` - Author name

### Prompt Engineering Guidelines
- Use clear, specific instructions for chapter structure
- Include word count targets and formatting requirements
- Provide context about target audience and writing style
- Include examples of desired output format
- Use Jinja2 variables for dynamic content insertion

### Error Handling
- Validate AI responses for proper format
- Retry generation with modified prompts if needed
- Log generation attempts and results in `_generated/`
- Provide fallback options for failed generations

## Publishing Integration

### KDP Preparation
- PDF output optimized for print specifications
- EPUB format for Kindle publishing
- Metadata extraction for KDP upload forms
- Cover image integration and sizing
- ISBN handling and registration guidance

### Output Formats
- **HTML**: GitHub Pages deployment, web reading
- **PDF**: Print-ready, KDP upload
- **EPUB**: E-reader compatibility, Kindle conversion
- **DOCX**: Manual editing, collaboration

## GitHub Pages Setup

The tool is designed to work seamlessly with GitHub Pages:
- Builds to `docs/` directory (standard GitHub Pages location)
- Includes `.nojekyll` file to bypass Jekyll processing
- HTML format optimized for web deployment
- Ready-to-deploy output structure

## Testing and Quality Assurance

### Content Quality
- Validate chapter coherence and flow
- Check for consistent tone and style
- Verify technical accuracy where applicable
- Test with different topics and templates

### Technical Testing
- Test all CLI commands in sequence
- Verify file generation and template processing
- Check build output in all formats
- Validate publishing-ready file formats

### Automation Testing
```bash
# Full pipeline test
cc-template new test-book --template non-fiction
cc-template outline test-book --topic "test topic"
# Edit outline.yml programmatically
cc-template generate test-book
cc-template build test-book --format all
# Verify output quality and format compliance
```