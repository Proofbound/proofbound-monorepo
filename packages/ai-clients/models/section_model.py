"""
Section model for table of contents.
"""

from typing import List
from pydantic import BaseModel, Field


class Section(BaseModel):
    section_name: str
    section_ideas: List[str] = Field(..., description="List of bullet-point ideas")