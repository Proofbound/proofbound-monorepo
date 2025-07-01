"""
Refactored AI-Powered Book Generator API.

This version uses a modular architecture with separate services for:
- AI client management
- PDF generation
- Cover generation
- Demo interface

Based on the CLAUDE.md roadmap for better maintainability and testing.
"""

import json
import time
from typing import List
from fastapi import FastAPI, HTTPException, Response, Query

# Import modular components
from models import (
    Section, TOCRequest, DraftRequest, PDFRequest, CoverRequest,
    ChapterRequest, ChapterResponse, BookGenerationRequest, BookGenerationResponse,
    BookContext, BookChaptersRequest, BookChaptersResponse
)
from services import ask_llm, ChapterGenerator, _PDF_AVAILABLE
try:
    from services import PDFGenerator, CoverGenerator
except ImportError:
    PDFGenerator = None
    CoverGenerator = None
from demo import demo_router

# Import mock data
from mock_data.responses import get_mock_response


# Performance tracking decorator
def track_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        if hasattr(result, '__dict__'):
            result.__dict__['_timing'] = duration
        return result
    return wrapper


# FastAPI app
app = FastAPI(
    title="AI-Powered Book Generator",
    description="Convert book ideas → TOC, draft, PDF, and cover via REST. Modular chapter-by-chapter architecture.",
)

# Include demo routes
app.include_router(demo_router)

# Initialize chapter generator
chapter_generator = ChapterGenerator(max_workers=5)


@app.get("/test")
def test_endpoint():
    """
    Simple test endpoint to verify the service is running.
    """
    import os
    return {
        "message": "AI Book Generator API is up and running!",
        "architecture": "modular_chapter_by_chapter",
        "available_endpoints": [
            "/toc", 
            "/draft", 
            "/generate-chapter", 
            "/generate-book", 
            "/generate-book-chapters",
            "/pdf", 
            "/cover", 
            "/demo", 
            "/demo/presets"
        ],
        "mock_endpoints": [
            "/mock/test",
            "/mock/toc",
            "/mock/draft", 
            "/mock/generate-chapter", 
            "/mock/generate-book", 
            "/mock/generate-book-chapters",
            "/mock/pdf",
            "/mock/cover"
        ],
        "debug_env": {
            "API_BASE_URL": os.getenv("API_BASE_URL", "NOT_SET"),
            "HAL9_TOKEN_present": "YES" if os.getenv("HAL9_TOKEN") else "NO"
        }
    }


@app.post("/toc", response_model=List[Section])
def generate_toc(req: TOCRequest):
    """Generate a JSON table of contents from title/author/idea."""
    prompt = (
        f"Act as an expert editor with the book idea: '{req.book_idea}'. "
        "Generate a detailed table of contents using the following JSON schema: "
        "[{\"section_name\": string, \"section_ideas\": [string, ...]}]. "
        "Create at least 10 sections, and include at least 10 section ideas per section. "
        "ONLY RETURN RAW JSON — do NOT include any Markdown formatting (no ``` or ```json), explanations, or extra text. "
        "The response must be directly parsable as JSON."
    )
    raw = ask_llm(prompt, default="[]")
    try:
        toc = json.loads(raw)
        if not isinstance(toc, list):
            raise ValueError
        return toc
    except ValueError:
        raise HTTPException(502, detail="LLM returned invalid JSON for TOC")


@app.post("/draft")
def generate_draft(req: DraftRequest):
    """Take a TOC + metadata, return a single Markdown string draft."""
    md = []
    count = 0

    for sec in req.toc:
        md.append(f"## {sec.section_name}\n")
        for idea in sec.section_ideas:
            count += 1
            prompt = (
                f"Act as an expert writer of the book '{req.title}' about '{req.book_idea}'. "
                f"Expand on '{idea}' in chapter '{sec.section_name}'. Write a couple of pages. "
                "Reply only with the contents of the section. Do not add chapter numbers or chapter titles."
            )
            content = ask_llm(prompt, default=f"*Error generating {idea}*")
            md.append(content + "\n\n")

    return {"markdown": "".join(md)}


@app.post("/pdf")
def generate_book_pdf(req: PDFRequest):
    """Convert Markdown + TOC + metadata → formatted PDF bytes."""
    if not _PDF_AVAILABLE or PDFGenerator is None:
        raise HTTPException(503, detail="PDF generation not available. WeasyPrint dependencies not installed.")
    
    try:
        pdf_bytes = PDFGenerator.generate_book_pdf(
            title=req.title,
            author=req.author,
            toc=req.toc,
            markdown=req.markdown
        )
        headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
        return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, detail=f"PDF generation failed: {str(e)}")


@app.post("/cover")
def generate_cover(req: CoverRequest):
    """Generate a full 6x9 cover PDF (front/back/spine) via AI + assemble."""
    if not _PDF_AVAILABLE or CoverGenerator is None:
        raise HTTPException(503, detail="Cover generation not available. WeasyPrint dependencies not installed.")
    
    try:
        pdf_bytes = CoverGenerator.generate_cover_pdf(
            title=req.title,
            author=req.author,
            book_idea=req.book_idea,
            num_pages=req.num_pages,
            include_spine_title=req.include_spine_title
        )
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(500, detail=f"Cover generation failed: {str(e)}")


@app.post("/generate-chapter", response_model=ChapterResponse)
def generate_chapter(req: ChapterRequest):
    """Generate a single chapter based on outline and context."""
    try:
        return chapter_generator.generate_single_chapter(req)
    except Exception as e:
        raise HTTPException(500, detail=f"Chapter generation failed: {str(e)}")


@app.post("/generate-book", response_model=BookGenerationResponse)
def generate_book(req: BookGenerationRequest):
    """Generate an entire book chapter by chapter with optional parallel processing."""
    try:
        return chapter_generator.generate_book(req)
    except Exception as e:
        raise HTTPException(500, detail=f"Book generation failed: {str(e)}")


@app.post("/generate-book-chapters", response_model=BookChaptersResponse)
def generate_book_chapters(req: BookChaptersRequest):
    """Generate TOC + selected chapters in one stateless call."""
    start_time = time.time()
    
    try:
        # Step 1: Generate TOC internally using the existing /toc logic
        toc_prompt = (
            f"Act as an expert editor with the book idea: '{req.book_idea}'. "
            "Generate a detailed table of contents using the following JSON schema: "
            "[{\"section_name\": string, \"section_ideas\": [string, ...]}]. "
            "Create at least 10 sections, and include at least 10 section ideas per section. "
            "ONLY RETURN RAW JSON — do NOT include any Markdown formatting (no ``` or ```json), explanations, or extra text. "
            "The response must be directly parsable as JSON."
        )
        toc_raw = ask_llm(toc_prompt, default="[]")
        toc_data = json.loads(toc_raw)
        
        if not isinstance(toc_data, list):
            raise ValueError("Invalid TOC format")
            
        # Convert to Section objects for chapter generation
        toc_sections = [Section(**section) for section in toc_data]
        
        # Step 2: Generate only the requested chapters
        chapters = []
        total_cost = 0.0
        
        book_context = BookContext(
            title=req.title,
            author=req.author,
            book_idea=req.book_idea
        )
        
        for chapter_num in req.chapters_to_generate:
            if chapter_num <= len(toc_sections):
                section = toc_sections[chapter_num - 1]
                
                # Create chapter outline from section
                from models.chapter_models import ChapterOutline
                chapter_outline = ChapterOutline(
                    chapter_number=chapter_num,
                    section_name=section.section_name,
                    section_ideas=section.section_ideas
                )
                
                # Generate chapter request
                chapter_request = ChapterRequest(
                    chapter_outline=chapter_outline,
                    book_context=book_context,
                    custom_instructions=f"This is chapter {chapter_num} of {len(toc_sections)} in the book. Generate with full context awareness."
                )
                
                # Generate the chapter
                chapter_response = chapter_generator.generate_single_chapter(chapter_request)
                chapters.append(chapter_response)
                
                if chapter_response.cost_estimate:
                    total_cost += chapter_response.cost_estimate
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return BookChaptersResponse(
            toc=toc_data,
            chapters=chapters,
            generated_chapters=req.chapters_to_generate,
            total_estimated_cost=total_cost,
            total_generation_time=total_time,
            metadata={
                "title": req.title,
                "author": req.author,
                "book_idea": req.book_idea,
                "total_chapters_in_toc": len(toc_sections),
                "chapters_requested": len(req.chapters_to_generate),
                "chapters_generated": len(chapters)
            }
        )
        
    except json.JSONDecodeError:
        raise HTTPException(502, detail="LLM returned invalid JSON for TOC")
    except Exception as e:
        raise HTTPException(500, detail=f"Book chapters generation failed: {str(e)}")


# Legacy draft endpoint for backwards compatibility
@app.post("/draft-legacy")
def generate_draft_legacy(req: DraftRequest):
    """Legacy monolithic draft generation - use /generate-book instead."""
    # Convert to new format
    book_context = BookContext(
        title=req.title,
        author=req.author,
        book_idea=req.book_idea
    )
    
    book_request = BookGenerationRequest(
        book_context=book_context,
        toc=req.toc,
        parallel_generation=False  # Sequential for consistency
    )
    
    try:
        book_response = chapter_generator.generate_book(book_request)
        # Combine all chapters into single markdown
        combined_markdown = "\n\n".join([
            f"## {chapter.section_name}\n\n{chapter.content}"
            for chapter in book_response.chapters
        ])
        
        return {
            "markdown": combined_markdown,
            "_metadata": {
                "generation_method": "chapter_by_chapter",
                "total_chapters": len(book_response.chapters),
                "total_words": book_response.total_word_count,
                "generation_time": book_response.total_generation_time,
                "cost_estimate": book_response.total_cost_estimate
            }
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Legacy draft generation failed: {str(e)}")


# ============================================================================
# MOCK ENDPOINTS - For testing without expensive AI calls
# ============================================================================

@app.get("/mock/test")
def mock_test_endpoint():
    """Mock version of /test endpoint."""
    return get_mock_response("test")


@app.post("/mock/toc", response_model=List[Section])
def mock_generate_toc(req: TOCRequest):
    """Mock version of /toc endpoint."""
    return get_mock_response("toc", req)


@app.post("/mock/draft")
def mock_generate_draft(req: DraftRequest):
    """Mock version of /draft endpoint."""
    return get_mock_response("draft", req)


@app.post("/mock/generate-chapter", response_model=ChapterResponse)
def mock_generate_chapter(req: ChapterRequest):
    """Mock version of /generate-chapter endpoint."""
    return get_mock_response("generate-chapter", req)


@app.post("/mock/generate-book", response_model=BookGenerationResponse)
def mock_generate_book(req: BookGenerationRequest):
    """Mock version of /generate-book endpoint."""
    return get_mock_response("generate-book", req)


@app.post("/mock/generate-book-chapters", response_model=BookChaptersResponse)
def mock_generate_book_chapters(req: BookChaptersRequest):
    """Mock version of /generate-book-chapters endpoint."""
    return get_mock_response("generate-book-chapters", req)


@app.post("/mock/pdf")
def mock_generate_book_pdf(req: PDFRequest):
    """Mock version of /pdf endpoint."""
    try:
        # Return the existing mock PDF file
        with open("mock_data/Eyes_on_Health_cover.pdf", "rb") as f:
            pdf_bytes = f.read()
        headers = {'Content-Disposition': 'inline; filename="mock_book.pdf"'}
        return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
    except FileNotFoundError:
        raise HTTPException(500, detail="Mock PDF file not found")


@app.post("/mock/cover")
def mock_generate_cover(req: CoverRequest):
    """Mock version of /cover endpoint."""
    try:
        # Return the existing mock cover PDF file
        with open("mock_data/Eyes_on_Health_cover.pdf", "rb") as f:
            pdf_bytes = f.read()
        filename = f"{req.title.replace(' ', '_')}_cover_mock.pdf"
        headers = {'Content-Disposition': f'inline; filename="{filename}"'}
        return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
    except FileNotFoundError:
        raise HTTPException(500, detail="Mock cover PDF file not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)