"""Prompt processing and template management."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class PromptProcessor:
    """Handles loading and processing of prompts with template variables."""

    def __init__(self, project_path: Path):
        """Initialize with project path."""
        self.project_path = Path(project_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration."""
        config_file = self.project_path / "cc-config.yml"
        if not config_file.exists():
            raise FileNotFoundError(f"No cc-config.yml found in {self.project_path}")

        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def load_prompt(
        self, prompt_name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Load and process a prompt with template variables."""
        # Try custom prompt override first
        if "prompts" in self.config and prompt_name in self.config["prompts"]:
            custom_prompt_path = self.project_path / self.config["prompts"][prompt_name]
            if custom_prompt_path.exists():
                prompt_content = custom_prompt_path.read_text()
            else:
                raise FileNotFoundError(
                    f"Custom prompt file not found: {custom_prompt_path}"
                )
        else:
            # Load from template prompts directory
            template_prompts_dir = self._get_template_prompts_dir()
            prompt_file = template_prompts_dir / f"{prompt_name}-prompt.txt"

            if not prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

            prompt_content = prompt_file.read_text()

        # Process template variables
        return self._process_template(prompt_content, context or {})

    def _get_template_prompts_dir(self) -> Path:
        """Get the prompts directory from the template backup."""
        templates_backup = self.project_path / ".templates"
        if not templates_backup.exists():
            raise FileNotFoundError(
                f"No .templates backup found in {self.project_path}"
            )

        prompts_dir = templates_backup / "prompts"
        if not prompts_dir.exists():
            raise FileNotFoundError(f"No prompts directory found in template backup")

        return prompts_dir

    def _process_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Process Jinja2 template with variables."""
        # Combine config variables with additional context
        template_vars = {**self.config, **context}

        # Create Jinja2 template and render
        env = Environment()
        template = env.from_string(template_content)
        return template.render(**template_vars)

    def get_available_prompts(self) -> list:
        """Get list of available prompt files."""
        prompts = []

        # Check template prompts directory
        try:
            template_prompts_dir = self._get_template_prompts_dir()
            for prompt_file in template_prompts_dir.glob("*-prompt.txt"):
                prompt_name = prompt_file.stem.replace("-prompt", "")
                prompts.append(prompt_name)
        except FileNotFoundError:
            pass

        # Check custom prompts in config
        if "prompts" in self.config:
            prompts.extend(self.config["prompts"].keys())

        return sorted(list(set(prompts)))

    def save_outline(self, outline_content: str) -> Path:
        """Save generated outline to outline.yml file."""
        outline_file = self.project_path / "outline.yml"

        # Validate YAML content
        try:
            yaml.safe_load(outline_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Generated outline is not valid YAML: {e}")

        outline_file.write_text(outline_content)
        return outline_file

    def load_outline(self) -> Dict[str, Any]:
        """Load existing outline.yml file."""
        outline_file = self.project_path / "outline.yml"
        if not outline_file.exists():
            raise FileNotFoundError(f"No outline.yml found in {self.project_path}")

        with open(outline_file, "r") as f:
            return yaml.safe_load(f)
