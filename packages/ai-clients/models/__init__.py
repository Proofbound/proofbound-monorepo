"""
Pydantic models for the AI Book Generator API.
"""

from .request_models import TOCRequest, DraftRequest, PDFRequest, CoverRequest
from .section_model import Section
from .chapter_models import (
    ChapterOutline, 
    BookContext, 
    ChapterRequest, 
    ChapterResponse, 
    BookGenerationRequest, 
    BookGenerationResponse,
    BookChaptersRequest,
    BookChaptersResponse
)

__all__ = [
    "Section", 
    "TOCRequest", 
    "DraftRequest", 
    "PDFRequest", 
    "CoverRequest",
    "ChapterOutline",
    "BookContext", 
    "ChapterRequest", 
    "ChapterResponse", 
    "BookGenerationRequest", 
    "BookGenerationResponse",
    "BookChaptersRequest",
    "BookChaptersResponse"
]