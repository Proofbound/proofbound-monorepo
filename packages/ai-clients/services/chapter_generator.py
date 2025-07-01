"""
Chapter-by-chapter generation service for better performance and cost optimization.
"""

import time
import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.chapter_models import (
    ChapterOutline, 
    BookContext, 
    ChapterRequest, 
    ChapterResponse, 
    BookGenerationRequest, 
    BookGenerationResponse
)
from models.section_model import Section
from .ai_client import ask_llm


class ChapterGenerator:
    """Service for generating book chapters individually or orchestrating complete books."""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize chapter generator.
        
        Args:
            max_workers: Maximum number of concurrent chapter generation threads
        """
        self.max_workers = max_workers
    
    def _estimate_cost(self, word_count: int, model: str = "gpt-4o") -> float:
        """
        Estimate cost based on word count and model.
        Rough estimates - update with actual pricing.
        """
        # Rough estimates for GPT-4o (update with actual pricing)
        tokens_per_word = 1.3  # Approximate
        tokens = word_count * tokens_per_word
        cost_per_1k_tokens = 0.005  # Example rate
        return (tokens / 1000) * cost_per_1k_tokens
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def generate_single_chapter(self, request: ChapterRequest) -> ChapterResponse:
        """
        Generate a single chapter based on outline and context.
        
        Args:
            request: Chapter generation request with outline and context
            
        Returns:
            Generated chapter response with content and metadata
        """
        start_time = time.time()
        
        # Build context-aware prompt
        context_parts = [
            f"You are writing chapter {request.chapter_outline.chapter_number} of the book '{request.book_context.title}' by {request.book_context.author}.",
            f"Book concept: {request.book_context.book_idea}",
            f"Chapter title: {request.chapter_outline.section_name}",
            f"Target length: {request.chapter_outline.target_length}",
        ]
        
        if request.book_context.genre:
            context_parts.append(f"Genre: {request.book_context.genre}")
        
        if request.book_context.writing_style:
            context_parts.append(f"Writing style: {request.book_context.writing_style}")
            
        if request.book_context.target_audience:
            context_parts.append(f"Target audience: {request.book_context.target_audience}")
        
        # Add chapter-specific content requirements
        ideas_text = "\\n".join(f"- {idea}" for idea in request.chapter_outline.section_ideas)
        context_parts.append(f"Key topics to cover:\\n{ideas_text}")
        
        # Add context from previous chapters if available
        if request.previous_chapters:
            prev_summary = "\\n".join(f"Chapter {i+1} summary: {ch[:200]}..." 
                                    for i, ch in enumerate(request.previous_chapters[-2:]))  # Last 2 chapters
            context_parts.append(f"Previous chapters context:\\n{prev_summary}")
        
        if request.custom_instructions:
            context_parts.append(f"Special instructions: {request.custom_instructions}")
        
        # Final instructions
        context_parts.extend([
            "Write engaging, well-structured content that flows naturally.",
            "Use markdown formatting with appropriate headers (## for main sections, ### for subsections).",
            "Do not include the chapter number or title in your response - just the content.",
            "Write in a style consistent with the book's overall tone and the specified genre."
        ])
        
        prompt = "\\n\\n".join(context_parts)
        
        # Generate the chapter
        content = ask_llm(prompt, default=f"*Error generating chapter {request.chapter_outline.chapter_number}*")
        
        # Calculate metrics
        generation_time = time.time() - start_time
        word_count = self._count_words(content)
        cost_estimate = self._estimate_cost(word_count)
        
        return ChapterResponse(
            chapter_number=request.chapter_outline.chapter_number,
            section_name=request.chapter_outline.section_name,
            content=content,
            word_count=word_count,
            generation_time=generation_time,
            cost_estimate=cost_estimate
        )
    
    def generate_book_sequential(self, request: BookGenerationRequest) -> BookGenerationResponse:
        """
        Generate an entire book chapter by chapter in sequence.
        Provides context from previous chapters for better coherence.
        
        Args:
            request: Book generation request with TOC and context
            
        Returns:
            Complete book with all chapters and generation metadata
        """
        start_time = time.time()
        chapters = []
        previous_chapters = []
        total_cost = 0.0
        
        for i, section in enumerate(request.toc, 1):
            chapter_outline = ChapterOutline(
                chapter_number=i,
                section_name=section.section_name,
                section_ideas=section.section_ideas
            )
            
            chapter_request = ChapterRequest(
                chapter_outline=chapter_outline,
                book_context=request.book_context,
                previous_chapters=previous_chapters.copy()  # Pass context from previous chapters
            )
            
            chapter_response = self.generate_single_chapter(chapter_request)
            chapters.append(chapter_response)
            
            # Add to context for next chapters (keep last 3 chapters for context)
            previous_chapters.append(chapter_response.content)
            if len(previous_chapters) > 3:
                previous_chapters.pop(0)
            
            if chapter_response.cost_estimate:
                total_cost += chapter_response.cost_estimate
        
        total_time = time.time() - start_time
        total_words = sum(ch.word_count for ch in chapters)
        
        return BookGenerationResponse(
            chapters=chapters,
            total_word_count=total_words,
            total_generation_time=total_time,
            total_cost_estimate=total_cost,
            generation_summary={
                "generation_method": "sequential",
                "chapters_generated": len(chapters),
                "average_words_per_chapter": total_words // len(chapters) if chapters else 0,
                "average_time_per_chapter": total_time / len(chapters) if chapters else 0,
                "context_maintained": True
            }
        )
    
    def generate_book_parallel(self, request: BookGenerationRequest) -> BookGenerationResponse:
        """
        Generate an entire book with chapters in parallel for speed.
        No cross-chapter context, but much faster for large books.
        
        Args:
            request: Book generation request with TOC and context
            
        Returns:
            Complete book with all chapters and generation metadata
        """
        start_time = time.time()
        chapters = [None] * len(request.toc)  # Pre-allocate list to maintain order
        total_cost = 0.0
        
        # Create chapter requests
        chapter_requests = []
        for i, section in enumerate(request.toc, 1):
            chapter_outline = ChapterOutline(
                chapter_number=i,
                section_name=section.section_name,
                section_ideas=section.section_ideas
            )
            
            chapter_request = ChapterRequest(
                chapter_outline=chapter_outline,
                book_context=request.book_context,
                previous_chapters=None  # No context in parallel mode
            )
            chapter_requests.append((i-1, chapter_request))  # Store index for ordering
        
        # Generate chapters in parallel
        max_workers = min(request.max_concurrent_chapters, self.max_workers, len(request.toc))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chapter generation tasks
            future_to_index = {
                executor.submit(self.generate_single_chapter, req): idx 
                for idx, req in chapter_requests
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    chapter_response = future.result()
                    chapters[idx] = chapter_response
                    if chapter_response.cost_estimate:
                        total_cost += chapter_response.cost_estimate
                except Exception as e:
                    # Create error chapter if generation fails
                    chapters[idx] = ChapterResponse(
                        chapter_number=idx + 1,
                        section_name=f"Chapter {idx + 1}",
                        content=f"*Error generating chapter: {str(e)}*",
                        word_count=0,
                        generation_time=0.0,
                        cost_estimate=0.0
                    )
        
        total_time = time.time() - start_time
        total_words = sum(ch.word_count for ch in chapters)
        
        return BookGenerationResponse(
            chapters=chapters,
            total_word_count=total_words,
            total_generation_time=total_time,
            total_cost_estimate=total_cost,
            generation_summary={
                "generation_method": "parallel",
                "chapters_generated": len(chapters),
                "max_concurrent_chapters": max_workers,
                "average_words_per_chapter": total_words // len(chapters) if chapters else 0,
                "average_time_per_chapter": total_time / len(chapters) if chapters else 0,
                "context_maintained": False
            }
        )
    
    def generate_book(self, request: BookGenerationRequest) -> BookGenerationResponse:
        """
        Generate a complete book using the specified method (parallel or sequential).
        
        Args:
            request: Book generation request
            
        Returns:
            Complete book generation response
        """
        if request.parallel_generation:
            return self.generate_book_parallel(request)
        else:
            return self.generate_book_sequential(request)
    
    def toc_to_chapter_outlines(self, toc: List[Section]) -> List[ChapterOutline]:
        """
        Convert TOC sections to chapter outlines.
        
        Args:
            toc: List of TOC sections
            
        Returns:
            List of chapter outlines
        """
        return [
            ChapterOutline(
                chapter_number=i,
                section_name=section.section_name,
                section_ideas=section.section_ideas
            )
            for i, section in enumerate(toc, 1)
        ]