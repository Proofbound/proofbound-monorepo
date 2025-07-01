"""
Models for chapter-by-chapter generation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .section_model import Section


class ChapterOutline(BaseModel):
    """Single chapter outline for generation."""
    chapter_number: int = Field(..., ge=1, description="Chapter number (1-based)")
    section_name: str = Field(..., description="Chapter/section name from TOC")
    section_ideas: List[str] = Field(..., description="Key ideas to cover in this chapter")
    target_length: Optional[str] = Field(default="2-3 pages", description="Target chapter length")


class BookContext(BaseModel):
    """Context information for maintaining consistency across chapters."""
    title: str
    author: str 
    book_idea: str
    genre: Optional[str] = Field(default=None, description="Book genre for tone consistency")
    writing_style: Optional[str] = Field(default=None, description="Specific writing style instructions")
    target_audience: Optional[str] = Field(default=None, description="Target audience for appropriate tone")


class ChapterRequest(BaseModel):
    """Request for generating a single chapter."""
    chapter_outline: ChapterOutline
    book_context: BookContext
    previous_chapters: Optional[List[str]] = Field(
        default=None, 
        description="Optional list of previously generated chapters for context"
    )
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Additional instructions for this specific chapter"
    )


class ChapterResponse(BaseModel):
    """Response containing a generated chapter."""
    chapter_number: int
    section_name: str
    content: str = Field(..., description="Generated chapter content in markdown")
    word_count: int = Field(..., description="Approximate word count")
    generation_time: Optional[float] = Field(default=None, description="Time taken to generate in seconds")
    cost_estimate: Optional[float] = Field(default=None, description="Estimated cost in USD")


class BookGenerationRequest(BaseModel):
    """Request for generating an entire book chapter by chapter."""
    book_context: BookContext
    toc: List[Section] = Field(..., description="Complete table of contents")
    parallel_generation: bool = Field(
        default=False, 
        description="Whether to generate chapters in parallel (faster but no cross-chapter context)"
    )
    max_concurrent_chapters: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of chapters to generate concurrently"
    )


class BookGenerationResponse(BaseModel):
    """Response for complete book generation."""
    chapters: List[ChapterResponse]
    total_word_count: int
    total_generation_time: float
    total_cost_estimate: Optional[float] = Field(default=None)
    generation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary stats and metadata about the generation process"
    )


class BookChaptersRequest(BaseModel):
    """Request model for generating TOC + selected chapters in one call"""
    title: str = Field(description="Book title")
    author: str = Field(description="Book author")
    book_idea: str = Field(description="Book concept/description")
    chapters_to_generate: List[int] = Field(default=[1], description="List of chapter numbers to generate (1-indexed)")


class BookChaptersResponse(BaseModel):
    """Response model for TOC + selected chapters generation"""
    toc: List[Dict[str, Any]] = Field(description="Generated table of contents")
    chapters: List[ChapterResponse] = Field(description="Generated chapter content")
    generated_chapters: List[int] = Field(description="Chapter numbers that were generated")
    total_estimated_cost: float = Field(description="Total cost for TOC + chapters")
    total_generation_time: float = Field(description="Total time for TOC + chapters")
    metadata: Dict[str, Any] = Field(description="Book metadata used for generation")