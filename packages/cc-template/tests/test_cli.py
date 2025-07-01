"""Tests for CLI commands."""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from cc_template.cli import main


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def runner():
    """Click test runner."""
    return CliRunner()


class TestNewCommand:
    """Tests for the 'new' command."""

    def test_new_command_creates_project(self, runner, temp_dir):
        """Test that new command creates a project directory."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            result = runner.invoke(main, ["new", project_name])

            assert result.exit_code == 0
            assert f"Creating new Quarto book project: {project_name}" in result.output
            assert "Project created successfully" in result.output

            # Check that project directory exists
            project_path = Path(project_name)
            assert project_path.exists()
            assert project_path.is_dir()

    def test_new_command_creates_required_files(self, runner):
        """Test that new command creates all required files."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            result = runner.invoke(main, ["new", project_name])

            assert result.exit_code == 0

            project_path = Path(project_name)
            expected_files = [
                "cc-config.yml",
                "_quarto.yml",
                "index.qmd",
                "intro.qmd",
                "summary.qmd",
                "references.qmd",
                "references.bib",
            ]

            for file_name in expected_files:
                file_path = project_path / file_name
                assert file_path.exists(), f"Expected file {file_name} not found"

    def test_new_command_creates_templates_backup(self, runner):
        """Test that new command creates .templates backup directory."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            result = runner.invoke(main, ["new", project_name])

            assert result.exit_code == 0

            project_path = Path(project_name)
            templates_backup = project_path / ".templates"
            assert templates_backup.exists()
            assert templates_backup.is_dir()

    def test_new_command_fails_if_directory_exists(self, runner):
        """Test that new command fails if target directory already exists."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            # Create directory first
            Path(project_name).mkdir()

            result = runner.invoke(main, ["new", project_name])

            assert result.exit_code == 0  # Command doesn't exit with error code
            assert "already exists" in result.output

    def test_new_command_with_custom_output_dir(self, runner):
        """Test new command with custom output directory."""
        project_name = "test-book"
        output_dir = "custom-output"

        with runner.isolated_filesystem():
            Path(output_dir).mkdir()

            result = runner.invoke(main, ["new", project_name, "--output", output_dir])

            assert result.exit_code == 0

            project_path = Path(output_dir) / project_name
            assert project_path.exists()
            assert project_path.is_dir()


class TestConfigCommand:
    """Tests for the 'config' command."""

    def test_config_command_processes_templates(self, runner):
        """Test that config command re-processes templates."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            # First create a project
            runner.invoke(main, ["new", project_name])

            # Then run config command
            result = runner.invoke(main, ["config", project_name])

            assert result.exit_code == 0
            assert "Re-processing templates" in result.output
            assert "Templates updated" in result.output

    def test_config_command_fails_without_config_file(self, runner):
        """Test that config command fails if no cc-config.yml exists."""
        project_name = "test-book"

        with runner.isolated_filesystem():
            Path(project_name).mkdir()

            result = runner.invoke(main, ["config", project_name])

            assert result.exit_code == 0  # Command doesn't exit with error code
            assert "No cc-config.yml found" in result.output


class TestBuildCommand:
    """Tests for the 'build' command."""

    def test_build_command_calls_quarto(self, runner, monkeypatch):
        """Test that build command attempts to call quarto."""
        project_name = "test-book"

        # Mock subprocess.run to avoid actually calling quarto
        import subprocess

        def mock_run(*args, **kwargs):
            # Mock successful quarto run
            result = subprocess.CompletedProcess(args=args[0], returncode=0)
            result.stdout = "Build successful"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        with runner.isolated_filesystem():
            # Create a project first
            runner.invoke(main, ["new", project_name])

            result = runner.invoke(main, ["build", project_name])

            assert result.exit_code == 0
            assert "Building Quarto book" in result.output
            assert "Book built successfully" in result.output

    def test_build_command_handles_quarto_not_found(self, runner, monkeypatch):
        """Test that build command handles quarto not being installed."""
        project_name = "test-book"

        # Mock subprocess.run to raise FileNotFoundError
        import subprocess

        def mock_run(*args, **kwargs):
            raise FileNotFoundError("quarto not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        with runner.isolated_filesystem():
            # Create a project first
            runner.invoke(main, ["new", project_name])

            result = runner.invoke(main, ["build", project_name])

            assert result.exit_code == 0
            assert "Quarto not found" in result.output
