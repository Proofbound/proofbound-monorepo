import pytest
from pydantic import ValidationError
from simple_app import Section, TOCRequest


class TestSection:
    """Test the Section Pydantic model."""

    def test_section_valid(self):
        """Test creating a valid Section."""
        section = Section(
            section_name="Test Chapter",
            section_ideas=["Idea 1", "Idea 2", "Idea 3"]
        )
        assert section.section_name == "Test Chapter"
        assert section.section_ideas == ["Idea 1", "Idea 2", "Idea 3"]

    def test_section_empty_ideas(self):
        """Test Section with empty section_ideas list."""
        section = Section(
            section_name="Empty Chapter",
            section_ideas=[]
        )
        assert section.section_name == "Empty Chapter"
        assert section.section_ideas == []

    def test_section_missing_name(self):
        """Test Section validation fails with missing section_name."""
        with pytest.raises(ValidationError) as exc_info:
            Section(section_ideas=["Idea 1", "Idea 2"])
        
        assert "section_name" in str(exc_info.value)

    def test_section_missing_ideas(self):
        """Test Section validation fails with missing section_ideas."""
        with pytest.raises(ValidationError) as exc_info:
            Section(section_name="Test Chapter")
        
        assert "section_ideas" in str(exc_info.value)

    def test_section_invalid_ideas_type(self):
        """Test Section validation fails with invalid section_ideas type."""
        with pytest.raises(ValidationError) as exc_info:
            Section(
                section_name="Test Chapter",
                section_ideas="not a list"
            )
        
        assert "section_ideas" in str(exc_info.value)

    def test_section_dict_conversion(self):
        """Test Section model dict conversion."""
        section = Section(
            section_name="Test Chapter",
            section_ideas=["Idea 1", "Idea 2"]
        )
        section_dict = section.model_dump()
        
        expected = {
            "section_name": "Test Chapter",
            "section_ideas": ["Idea 1", "Idea 2"]
        }
        assert section_dict == expected


class TestTOCRequest:
    """Test the TOCRequest Pydantic model."""

    def test_toc_request_valid(self):
        """Test creating a valid TOCRequest."""
        request = TOCRequest(
            title="Test Book",
            author="Test Author",
            book_idea="A book about testing"
        )
        assert request.title == "Test Book"
        assert request.author == "Test Author"
        assert request.book_idea == "A book about testing"

    def test_toc_request_missing_title(self):
        """Test TOCRequest validation fails with missing title."""
        with pytest.raises(ValidationError) as exc_info:
            TOCRequest(
                author="Test Author",
                book_idea="A book about testing"
            )
        
        assert "title" in str(exc_info.value)

    def test_toc_request_missing_author(self):
        """Test TOCRequest validation fails with missing author."""
        with pytest.raises(ValidationError) as exc_info:
            TOCRequest(
                title="Test Book",
                book_idea="A book about testing"
            )
        
        assert "author" in str(exc_info.value)

    def test_toc_request_missing_book_idea(self):
        """Test TOCRequest validation fails with missing book_idea."""
        with pytest.raises(ValidationError) as exc_info:
            TOCRequest(
                title="Test Book",
                author="Test Author"
            )
        
        assert "book_idea" in str(exc_info.value)

    def test_toc_request_empty_strings(self):
        """Test TOCRequest with empty strings (should be valid)."""
        request = TOCRequest(
            title="",
            author="",
            book_idea=""
        )
        assert request.title == ""
        assert request.author == ""
        assert request.book_idea == ""

    def test_toc_request_whitespace(self):
        """Test TOCRequest with whitespace strings."""
        request = TOCRequest(
            title="   Test Book   ",
            author="  Test Author  ",
            book_idea="  A book idea  "
        )
        assert request.title == "   Test Book   "
        assert request.author == "  Test Author  "
        assert request.book_idea == "  A book idea  "

    def test_toc_request_dict_conversion(self):
        """Test TOCRequest model dict conversion."""
        request = TOCRequest(
            title="Test Book",
            author="Test Author",
            book_idea="A book about testing"
        )
        request_dict = request.model_dump()
        
        expected = {
            "title": "Test Book",
            "author": "Test Author",
            "book_idea": "A book about testing"
        }
        assert request_dict == expected

    def test_toc_request_from_dict(self):
        """Test creating TOCRequest from dictionary."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "book_idea": "A book about testing"
        }
        request = TOCRequest(**data)
        
        assert request.title == "Test Book"
        assert request.author == "Test Author"
        assert request.book_idea == "A book about testing"