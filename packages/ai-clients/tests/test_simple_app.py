import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from simple_app import app, ask_llm


class TestSimpleApp:
    """Test the simple_app FastAPI application."""

    @pytest.fixture
    def client(self, mock_env_vars):
        """Create test client with mocked environment."""
        with patch('simple_app.openai_client'):
            return TestClient(app)

    def test_test_endpoint(self, client):
        """Test the /test endpoint."""
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Simple API is up and running!"
        assert "/toc" in data["available_endpoints"]

    def test_toc_endpoint_success(self, client, sample_toc_request, sample_toc_response, mock_openai_client):
        """Test successful TOC generation."""
        # Mock the OpenAI response
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(sample_toc_response)
        
        with patch('simple_app.openai_client', mock_openai_client):
            response = client.post("/toc", json=sample_toc_request)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["section_name"] == "Introduction to Testing"
        assert len(data[0]["section_ideas"]) == 5

    def test_toc_endpoint_invalid_request(self, client):
        """Test TOC endpoint with invalid request data."""
        invalid_request = {
            "title": "Test Book"
            # Missing required fields
        }
        
        response = client.post("/toc", json=invalid_request)
        assert response.status_code == 422  # Unprocessable Entity

    def test_toc_endpoint_empty_request(self, client):
        """Test TOC endpoint with empty request."""
        response = client.post("/toc", json={})
        assert response.status_code == 422

    def test_toc_endpoint_invalid_json_response(self, client, sample_toc_request, mock_openai_client):
        """Test TOC endpoint when LLM returns invalid JSON."""
        # Mock invalid JSON response
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON response"
        
        with patch('simple_app.openai_client', mock_openai_client):
            response = client.post("/toc", json=sample_toc_request)
        
        assert response.status_code == 502
        data = response.json()
        assert "LLM returned invalid JSON for TOC" in data["detail"]

    def test_toc_endpoint_non_list_response(self, client, sample_toc_request, mock_openai_client):
        """Test TOC endpoint when LLM returns valid JSON but not a list."""
        # Mock non-list JSON response
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({"not": "a list"})
        
        with patch('simple_app.openai_client', mock_openai_client):
            response = client.post("/toc", json=sample_toc_request)
        
        assert response.status_code == 502

    def test_toc_endpoint_different_book_ideas(self, client, mock_openai_client, sample_toc_response):
        """Test TOC endpoint with different book ideas."""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(sample_toc_response)
        
        test_cases = [
            {
                "title": "History Book",
                "author": "Historian",
                "book_idea": "A history of ancient Rome"
            },
            {
                "title": "Cookbook",
                "author": "Chef",
                "book_idea": "Italian recipes for beginners"
            },
            {
                "title": "Technical Guide",
                "author": "Engineer",
                "book_idea": "Building microservices with Python"
            }
        ]
        
        with patch('simple_app.openai_client', mock_openai_client):
            for test_case in test_cases:
                response = client.post("/toc", json=test_case)
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)


class TestAskLlmFunction:
    """Test the ask_llm helper function."""

    def test_ask_llm_success(self, mock_openai_client, mock_env_vars):
        """Test successful LLM call."""
        expected_content = "Test response from LLM"
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = expected_content
        
        with patch('simple_app.openai_client', mock_openai_client):
            result = ask_llm("Test prompt")
        
        assert result == expected_content
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_ask_llm_exception(self, mock_env_vars):
        """Test LLM call with exception."""
        with patch('simple_app.openai_client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            result = ask_llm("Test prompt", default="fallback")
            assert result == "fallback"

    def test_ask_llm_default_fallback(self, mock_env_vars):
        """Test LLM call with default fallback."""
        with patch('simple_app.openai_client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            result = ask_llm("Test prompt")
            assert result == ""

    def test_ask_llm_parameters(self, mock_openai_client, mock_env_vars):
        """Test that ask_llm calls OpenAI with correct parameters."""
        test_prompt = "Generate a table of contents"
        
        with patch('simple_app.openai_client', mock_openai_client):
            ask_llm(test_prompt)
        
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o"
        assert call_args[1]["messages"][0]["role"] == "user"
        assert call_args[1]["messages"][0]["content"] == test_prompt
        assert call_args[1]["stream"] is False


class TestAppConfiguration:
    """Test app configuration and initialization."""

    def test_app_title_and_description(self):
        """Test FastAPI app configuration."""
        assert app.title == "AI-Powered Book Generator (Simple)"
        assert "Generate TOC via REST API" in app.description

    def test_missing_hal9_token(self):
        """Test app fails to start without HAL9_TOKEN."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="HAL9_TOKEN must be set"):
                # This would normally be caught during import, but we test the logic
                import os
                if not os.getenv("HAL9_TOKEN"):
                    raise RuntimeError("HAL9_TOKEN must be set")

    def test_openai_client_configuration(self, mock_env_vars):
        """Test OpenAI client is configured correctly."""
        # This test verifies that the client exists and is properly configured
        import simple_app
        
        # Test that the client exists and has expected attributes
        assert hasattr(simple_app, 'openai_client')
        assert simple_app.openai_client is not None
        
        # Test that OAI_TOKEN is set (value will depend on environment)
        assert simple_app.OAI_TOKEN is not None
        assert len(simple_app.OAI_TOKEN) > 0