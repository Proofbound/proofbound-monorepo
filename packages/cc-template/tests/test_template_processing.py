"""Tests for template processing functionality."""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from cc_template.cli import _process_config_and_templates, _apply_template_variables


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Sample configuration data."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "topic": "Testing Templates",
        "writing_style": "technical",
    }


@pytest.fixture
def sample_project(temp_dir, sample_config):
    """Create a sample project structure for testing."""
    project_path = temp_dir / "test-project"
    project_path.mkdir()

    # Create config file
    config_file = project_path / "cc-config.yml"
    config_file.write_text(yaml.dump(sample_config))

    # Create .templates directory with sample template files
    templates_dir = project_path / ".templates"
    templates_dir.mkdir()

    # Sample template file with Jinja2 variables
    template_content = """---
title: "{{title}}"
author: "{{author}}"
---

# {{title}}

This book about {{topic}} is written by {{author}}.
"""

    sample_template = templates_dir / "index.qmd"
    sample_template.write_text(template_content)

    # Non-template file (should be copied as-is)
    binary_file = templates_dir / "image.png"
    binary_file.write_bytes(b"fake image data")

    return project_path


class TestConfigProcessing:
    """Tests for configuration processing."""

    def test_process_config_and_templates(self, sample_project):
        """Test basic config processing."""
        _process_config_and_templates(sample_project, "test-project")

        # Check that template file was processed
        output_file = sample_project / "index.qmd"
        assert output_file.exists()

        content = output_file.read_text()
        assert 'title: "Test Book"' in content
        assert 'author: "Test Author"' in content
        assert "This book about Testing Templates" in content

    def test_config_with_project_variables(self, temp_dir):
        """Test config processing with built-in variables."""
        project_path = temp_dir / "my-project"
        project_path.mkdir()

        # Create config with project_name variable
        config_content = """title: "{{project_name}} Guide"
author: "Test Author"
date: "{{current_date}}"
"""
        config_file = project_path / "cc-config.yml"
        config_file.write_text(config_content)

        # Create template backup
        templates_dir = project_path / ".templates"
        templates_dir.mkdir()

        template_content = """# {{title}}
Created on {{date}}
"""
        (templates_dir / "index.qmd").write_text(template_content)

        _process_config_and_templates(project_path, "my-project")

        # Check processed config
        processed_config = yaml.safe_load(config_file.read_text())
        assert processed_config["title"] == "my-project Guide"
        assert "date" in processed_config

        # Check processed template
        output_file = project_path / "index.qmd"
        content = output_file.read_text()
        assert "my-project Guide" in content


class TestTemplateVariables:
    """Tests for template variable application."""

    def test_apply_template_variables(self, sample_project, sample_config):
        """Test applying variables to template files."""
        template_vars = {
            "project_name": "test-project",
            "current_date": "2023-01-01",
            **sample_config,
        }

        _apply_template_variables(sample_project, template_vars)

        output_file = sample_project / "index.qmd"
        assert output_file.exists()

        content = output_file.read_text()
        assert 'title: "Test Book"' in content
        assert 'author: "Test Author"' in content
        assert "This book about Testing Templates is written by Test Author" in content

    def test_non_template_files_copied_as_is(self, sample_project, sample_config):
        """Test that non-template files are copied without processing."""
        template_vars = {"title": "Test Book"}

        _apply_template_variables(sample_project, template_vars)

        # Check that binary file was copied unchanged
        output_file = sample_project / "image.png"
        assert output_file.exists()
        assert output_file.read_bytes() == b"fake image data"

    def test_only_files_with_jinja_variables_processed(self, temp_dir):
        """Test that only files with Jinja2 variables are processed."""
        project_path = temp_dir / "test-project"
        project_path.mkdir()

        templates_dir = project_path / ".templates"
        templates_dir.mkdir()

        # File with Jinja2 variables
        template_file = templates_dir / "with_vars.qmd"
        template_file.write_text("Title: {{title}}")

        # File without Jinja2 variables
        static_file = templates_dir / "no_vars.qmd"
        static_file.write_text("Static content here")

        template_vars = {"title": "Test Title"}
        _apply_template_variables(project_path, template_vars)

        # Check processed file
        processed = project_path / "with_vars.qmd"
        assert processed.read_text() == "Title: Test Title"

        # Check static file
        static = project_path / "no_vars.qmd"
        assert static.read_text() == "Static content here"

    def test_handles_missing_templates_backup(self, temp_dir):
        """Test graceful handling when .templates backup is missing."""
        project_path = temp_dir / "test-project"
        project_path.mkdir()

        # No .templates directory exists
        template_vars = {"title": "Test"}

        # Should not raise an exception
        _apply_template_variables(project_path, template_vars)


class TestYAMLProcessing:
    """Tests for YAML file processing."""

    def test_yaml_files_processed(self, temp_dir):
        """Test that YAML files are processed with template variables."""
        project_path = temp_dir / "test-project"
        project_path.mkdir()

        templates_dir = project_path / ".templates"
        templates_dir.mkdir()

        yaml_content = """project:
  title: "{{title}}"
  author: "{{author}}"
  settings:
    theme: default
"""

        yaml_file = templates_dir / "_quarto.yml"
        yaml_file.write_text(yaml_content)

        template_vars = {"title": "My Great Book", "author": "Jane Doe"}

        _apply_template_variables(project_path, template_vars)

        output_file = project_path / "_quarto.yml"
        processed_yaml = yaml.safe_load(output_file.read_text())

        assert processed_yaml["project"]["title"] == "My Great Book"
        assert processed_yaml["project"]["author"] == "Jane Doe"
        assert processed_yaml["project"]["settings"]["theme"] == "default"
