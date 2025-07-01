#!/usr/bin/env python3
"""
Test script for mock endpoints functionality.
This tests the mock endpoints without requiring WeasyPrint or HAL9_TOKEN.
"""

import sys
import os
sys.path.append('.')

# Test imports
try:
    from mock_data.responses import get_mock_response
    print("✅ Mock response system imported successfully")
except ImportError as e:
    print(f"❌ Failed to import mock responses: {e}")
    sys.exit(1)

try:
    from models.request_models import TOCRequest
    from models.chapter_models import BookChaptersRequest, ChapterRequest, ChapterOutline, BookContext
    from models.section_model import Section
    print("✅ Model imports successful")
except ImportError as e:
    print(f"❌ Failed to import models: {e}")
    sys.exit(1)

# Test FastAPI app creation with mock endpoints
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from typing import List
    
    # Create minimal test app with just mock endpoints
    app = FastAPI(title="Mock Endpoint Test")
    
    @app.get("/mock/test")
    def mock_test():
        return get_mock_response("test")
    
    @app.post("/mock/toc", response_model=List[Section])
    def mock_toc(req: TOCRequest):
        return get_mock_response("toc", req)
    
    @app.post("/mock/generate-book-chapters")
    def mock_book_chapters(req: BookChaptersRequest):
        return get_mock_response("generate-book-chapters", req)
    
    @app.post("/mock/generate-chapter")
    def mock_chapter(req: ChapterRequest):
        return get_mock_response("generate-chapter", req)
    
    print("✅ Test FastAPI app created successfully")
    
    # Test the endpoints
    client = TestClient(app)
    
    print("\n=== Testing Mock Endpoints ===")
    
    # Test mock test endpoint
    response = client.get("/mock/test")
    assert response.status_code == 200
    data = response.json()
    assert data["mock_mode"] == True
    print("✅ /mock/test endpoint working")
    
    # Test mock TOC endpoint
    response = client.post("/mock/toc", json={
        "title": "Test Book",
        "author": "Test Author",
        "book_idea": "Test concept about AI and health"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10  # Should have 10 TOC sections
    assert "section_name" in data[0]
    assert "section_ideas" in data[0]
    print("✅ /mock/toc endpoint working")
    
    # Test mock book chapters endpoint
    response = client.post("/mock/generate-book-chapters", json={
        "title": "Test Book",
        "author": "Test Author", 
        "book_idea": "Test concept",
        "chapters_to_generate": [1, 2]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["chapters"]) == 2
    assert len(data["toc"]) == 10
    assert data["total_estimated_cost"] > 0
    print("✅ /mock/generate-book-chapters endpoint working")
    
    # Test mock generate-chapter endpoint
    response = client.post("/mock/generate-chapter", json={
        "chapter_outline": {
            "chapter_number": 3,
            "section_name": "Test Chapter",
            "section_ideas": ["Test idea 1", "Test idea 2", "Test idea 3"]
        },
        "book_context": {
            "title": "Test Book",
            "author": "Test Author",
            "book_idea": "Test concept"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert data["chapter_number"] == 3
    assert data["section_name"] == "Test Chapter"
    assert data["word_count"] > 0
    print("✅ /mock/generate-chapter endpoint working")
    
    print("\n🎉 All mock endpoints are working correctly!")
    print("\nUsage Examples:")
    print("- GET  /mock/test")
    print("- POST /mock/toc")
    print("- POST /mock/draft") 
    print("- POST /mock/generate-chapter")
    print("- POST /mock/generate-book")
    print("- POST /mock/generate-book-chapters")
    print("- POST /mock/pdf")
    print("- POST /mock/cover")
    print("\nDemo interface includes mock mode toggle for easy testing!")
    
except Exception as e:
    print(f"❌ FastAPI test failed: {e}")
    sys.exit(1)