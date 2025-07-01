"""
Business logic services for the AI Book Generator.
"""

from .ai_client import get_openai_client, get_replicate_client, ask_llm
from .chapter_generator import ChapterGenerator

# Import WeasyPrint-dependent services only when needed
try:
    from .pdf_generator import PDFGenerator
    from .cover_generator import CoverGenerator
    _PDF_AVAILABLE = True
except ImportError:
    PDFGenerator = None
    CoverGenerator = None
    _PDF_AVAILABLE = False

__all__ = [
    "get_openai_client",
    "get_replicate_client", 
    "ask_llm",
    "ChapterGenerator",
    "PDFGenerator",
    "CoverGenerator",
    "_PDF_AVAILABLE"
]