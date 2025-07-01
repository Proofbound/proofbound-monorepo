"""Tests for outline command and AI integration."""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from click.testing import CliRunner

from cc_template.cli import main
from cc_template.ai_client import AIClient
from cc_template.prompt_processor import PromptProcessor


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_project(temp_dir):
    """Create a sample project for testing."""
    project_path = temp_dir / "test-book"

    # Create project structure
    project_path.mkdir()

    # Create config file
    config = {
        "title": "Test Book",
        "author": "Test Author",
        "topic": "AI and Machine Learning",
        "writing_style": "technical but accessible",
    }

    config_file = project_path / "cc-config.yml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)

    # Create .templates directory with prompts
    templates_dir = project_path / ".templates"
    templates_dir.mkdir()

    prompts_dir = templates_dir / "prompts"
    prompts_dir.mkdir()

    # Create outline prompt
    outline_prompt = """Generate an outline for: {{topic}}
Writing style: {{writing_style}}

Create chapters covering the topic thoroughly."""

    (prompts_dir / "outline-prompt.txt").write_text(outline_prompt)

    return project_path


@pytest.fixture
def runner():
    """Click test runner."""
    return CliRunner()


class TestPromptProcessor:
    """Tests for PromptProcessor class."""

    def test_load_config(self, sample_project):
        """Test loading project configuration."""
        processor = PromptProcessor(sample_project)
        config = processor.config

        assert config["title"] == "Test Book"
        assert config["author"] == "Test Author"
        assert config["topic"] == "AI and Machine Learning"

    def test_load_prompt(self, sample_project):
        """Test loading and processing prompts."""
        processor = PromptProcessor(sample_project)

        prompt = processor.load_prompt("outline")

        assert "AI and Machine Learning" in prompt
        assert "technical but accessible" in prompt

    def test_load_prompt_with_context(self, sample_project):
        """Test loading prompt with additional context."""
        processor = PromptProcessor(sample_project)

        context = {"topic": "Custom Topic Override"}
        prompt = processor.load_prompt("outline", context)

        assert "Custom Topic Override" in prompt

    def test_save_outline(self, sample_project):
        """Test saving outline content."""
        processor = PromptProcessor(sample_project)

        outline_content = """book:
  title: "Test Book"
  description: "Test description"
  
chapters:
  - id: "intro"
    title: "Introduction"
    description: "Introduction chapter"
    target_words: 3000
    status: "pending"
"""

        outline_file = processor.save_outline(outline_content)

        assert outline_file.exists()
        assert outline_file.name == "outline.yml"

        # Verify content is valid YAML
        with open(outline_file, "r") as f:
            loaded_outline = yaml.safe_load(f)

        assert loaded_outline["book"]["title"] == "Test Book"
        assert len(loaded_outline["chapters"]) == 1

    def test_save_invalid_yaml_raises_error(self, sample_project):
        """Test that saving invalid YAML raises error."""
        processor = PromptProcessor(sample_project)

        invalid_yaml = "this is not: valid: yaml: content:"

        with pytest.raises(ValueError, match="not valid YAML"):
            processor.save_outline(invalid_yaml)

    def test_get_available_prompts(self, sample_project):
        """Test getting list of available prompts."""
        processor = PromptProcessor(sample_project)

        prompts = processor.get_available_prompts()

        assert "outline" in prompts


class TestAIClient:
    """Tests for AIClient class."""

    def test_detect_provider_openai(self, monkeypatch):
        """Test provider detection with OpenAI key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with patch("cc_template.ai_client.OPENAI_AVAILABLE", True):
            client = AIClient()
            assert client.provider == "openai"

    def test_detect_provider_anthropic(self, monkeypatch):
        """Test provider detection with Anthropic key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        with patch("cc_template.ai_client.ANTHROPIC_AVAILABLE", True):
            client = AIClient()
            assert client.provider == "anthropic"

    def test_no_provider_raises_error(self, monkeypatch):
        """Test that missing API keys raise error."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="No AI provider configured"):
            AIClient()

    @patch("cc_template.ai_client.openai")
    def test_openai_content_generation(self, mock_openai, monkeypatch):
        """Test content generation with OpenAI."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated outline content"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        with patch("cc_template.ai_client.OPENAI_AVAILABLE", True):
            client = AIClient("openai")
            result = client.generate_content("Test prompt")

            assert result == "Generated outline content"
            mock_client.chat.completions.create.assert_called_once()

    @patch("cc_template.ai_client.anthropic")
    def test_anthropic_content_generation(self, mock_anthropic, monkeypatch):
        """Test content generation with Anthropic."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Mock Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Generated outline content"

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        with patch("cc_template.ai_client.ANTHROPIC_AVAILABLE", True):
            client = AIClient("anthropic")
            result = client.generate_content("Test prompt")

            assert result == "Generated outline content"
            mock_client.messages.create.assert_called_once()


class TestOutlineCommand:
    """Tests for the outline CLI command."""

    @patch("cc_template.ai_client.create_ai_client")
    def test_outline_command_success(
        self, mock_create_ai_client, runner, sample_project
    ):
        """Test successful outline generation."""
        # Mock AI client
        mock_ai_client = Mock()
        mock_ai_client.generate_content.return_value = """```yaml
book:
  title: "Test Book"
  description: "AI and Machine Learning"
  target_length: 50000
  
chapters:
  - id: "intro"
    title: "Introduction to AI"
    description: "Overview of artificial intelligence"
    target_words: 3500
    status: "pending"
    prompt_context:
      focus: "foundations"
      tone: "technical but accessible"
```"""

        mock_create_ai_client.return_value = mock_ai_client

        # Run outline command
        result = runner.invoke(
            main, ["outline", str(sample_project), "--topic", "AI and Machine Learning"]
        )

        assert result.exit_code == 0
        assert "Generating outline for project" in result.output
        assert "Outline generated and saved" in result.output

        # Check that outline.yml was created
        outline_file = sample_project / "outline.yml"
        assert outline_file.exists()

        # Verify content
        with open(outline_file, "r") as f:
            outline = yaml.safe_load(f)

        assert outline["book"]["title"] == "Test Book"
        assert len(outline["chapters"]) == 1

    def test_outline_command_missing_project(self, runner):
        """Test outline command with missing project."""
        result = runner.invoke(main, ["outline", "nonexistent-project"])

        assert result.exit_code == 2  # Click error for missing path

    @patch("cc_template.ai_client.create_ai_client")
    def test_outline_command_with_provider(
        self, mock_create_ai_client, runner, sample_project
    ):
        """Test outline command with specific provider."""
        mock_ai_client = Mock()
        mock_ai_client.generate_content.return_value = "book:\n  title: Test"
        mock_create_ai_client.return_value = mock_ai_client

        result = runner.invoke(
            main, ["outline", str(sample_project), "--provider", "openai"]
        )

        assert result.exit_code == 0
        mock_create_ai_client.assert_called_once_with("openai")

    def test_outline_updates_config_topic(self, runner, sample_project):
        """Test that outline command updates topic in config."""
        with patch("cc_template.ai_client.create_ai_client") as mock_create_ai_client:
            mock_ai_client = Mock()
            mock_ai_client.generate_content.return_value = "book:\n  title: Test"
            mock_create_ai_client.return_value = mock_ai_client

            result = runner.invoke(
                main, ["outline", str(sample_project), "--topic", "New Custom Topic"]
            )

            assert result.exit_code == 0

            # Check that config was updated
            config_file = sample_project / "cc-config.yml"
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            assert config["topic"] == "New Custom Topic"
