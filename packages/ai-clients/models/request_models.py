"""
Request models for API endpoints.
"""

from typing import List
from pydantic import BaseModel, Field
from .section_model import Section


class TOCRequest(BaseModel):
    title: str
    author: str
    book_idea: str


class DraftRequest(BaseModel):
    title: str
    author: str
    book_idea: str
    toc: List[Section]


class PDFRequest(BaseModel):
    title: str
    author: str
    toc: List[Section]
    markdown: str


class CoverRequest(BaseModel):
    title: str
    author: str
    book_idea: str
    num_pages: int = Field(..., gt=0)
    include_spine_title: bool = False