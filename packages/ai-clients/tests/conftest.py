import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from typing import Generator, Dict, Any

# Test fixtures for common request/response data
@pytest.fixture
def sample_toc_request() -> Dict[str, str]:
    """Sample TOC request data for testing."""
    return {
        "title": "Test Book Title",
        "author": "Test Author",
        "book_idea": "A comprehensive guide to testing FastAPI applications"
    }

@pytest.fixture
def sample_toc_response() -> list:
    """Sample TOC response data for testing."""
    return [
        {
            "section_name": "Introduction to Testing",
            "section_ideas": [
                "Why testing matters",
                "Types of testing",
                "Testing frameworks",
                "Best practices",
                "Common pitfalls"
            ]
        },
        {
            "section_name": "FastAPI Testing",
            "section_ideas": [
                "Setting up test environment",
                "Testing endpoints",
                "Mocking dependencies",
                "Async testing",
                "Integration tests"
            ]
        }
    ]

@pytest.fixture
def mock_openai_response() -> Mock:
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_choice = Mock()
    mock_choice.message.content = json.dumps([
        {
            "section_name": "Test Section",
            "section_ideas": ["Test idea 1", "Test idea 2", "Test idea 3"]
        }
    ])
    mock_response.choices = [mock_choice]
    return mock_response

@pytest.fixture
def mock_openai_client(mock_openai_response) -> Generator[Mock, None, None]:
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_openai_response
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_replicate_client() -> Generator[Mock, None, None]:
    """Mock Replicate client for testing."""
    with patch('replicate.client.Client') as mock_client:
        mock_instance = Mock()
        # Mock image generation response
        mock_instance.run.return_value = ["https://example.com/test-image.jpg"]
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    with patch.dict('os.environ', {'HAL9_TOKEN': 'test-token-123'}):
        yield

@pytest.fixture
def sample_draft_request() -> Dict[str, Any]:
    """Sample draft request data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "book_idea": "Test book idea",
        "toc": [
            {
                "section_name": "Chapter 1",
                "section_ideas": ["Idea 1", "Idea 2"]
            }
        ]
    }

@pytest.fixture
def sample_pdf_request() -> Dict[str, str]:
    """Sample PDF request data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "markdown_content": "# Chapter 1\n\nThis is test content.\n\n## Section 1.1\n\nMore test content."
    }

@pytest.fixture
def sample_cover_request() -> Dict[str, str]:
    """Sample cover request data for testing."""
    return {
        "title": "Test Book Title",
        "author": "Test Author Name",
        "subtitle": "A Test Subtitle"
    }

@pytest.fixture
def mock_weasyprint() -> Generator[Mock, None, None]:
    """Mock WeasyPrint for PDF generation testing."""
    with patch('weasyprint.HTML') as mock_html:
        mock_instance = Mock()
        mock_instance.write_pdf.return_value = b'fake-pdf-content'
        mock_html.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_pypandoc() -> Generator[Mock, None, None]:
    """Mock pypandoc for markdown conversion testing."""
    with patch('pypandoc.convert_text') as mock_convert:
        mock_convert.return_value = "<h1>Test HTML</h1><p>Test content</p>"
        yield mock_convert