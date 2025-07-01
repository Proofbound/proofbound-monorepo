"""
Example of polling-based progress tracking.
"""

import uuid
import time
from typing import Dict, Any
from fastapi import BackgroundTasks

# In-memory progress store (use Redis in production)
progress_store: Dict[str, Dict[str, Any]] = {}

@app.post("/generate-book-chapters-async")
async def start_book_generation(req: BookChaptersRequest, background_tasks: BackgroundTasks):
    """Start book generation and return job ID for polling."""
    job_id = str(uuid.uuid4())
    
    # Initialize progress
    progress_store[job_id] = {
        'status': 'started',
        'progress': 0,
        'step': 'initializing',
        'message': 'Starting book generation...',
        'result': None,
        'error': None,
        'created_at': time.time()
    }
    
    # Start background task
    background_tasks.add_task(generate_book_background, job_id, req)
    
    return {'job_id': job_id, 'status': 'started'}

@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """Check progress of a book generation job."""
    if job_id not in progress_store:
        raise HTTPException(404, detail="Job not found")
    
    return progress_store[job_id]

async def generate_book_background(job_id: str, req: BookChaptersRequest):
    """Background task for book generation with progress updates."""
    try:
        # Update progress: TOC generation
        progress_store[job_id].update({
            'status': 'running',
            'progress': 10,
            'step': 'toc',
            'message': 'Generating table of contents...'
        })
        
        # Generate TOC (replace with actual call)
        time.sleep(2)  # Simulate AI call
        toc_data = [{"section_name": "Chapter 1", "section_ideas": ["idea1"]}]
        
        # Update progress: Chapters
        total_chapters = len(req.chapters_to_generate)
        chapters = []
        
        for i, chapter_num in enumerate(req.chapters_to_generate):
            progress = 10 + (i + 1) / total_chapters * 80  # 10% for TOC, 80% for chapters
            
            progress_store[job_id].update({
                'progress': progress,
                'step': 'chapter',
                'message': f'Generating chapter {chapter_num} of {total_chapters}...'
            })
            
            # Generate chapter (replace with actual call)
            time.sleep(3)  # Simulate AI call
            chapter_data = {
                'chapter_number': chapter_num,
                'content': f'Chapter {chapter_num} content...',
                'word_count': 500
            }
            chapters.append(chapter_data)
        
        # Complete
        progress_store[job_id].update({
            'status': 'completed',
            'progress': 100,
            'step': 'complete',
            'message': 'Book generation complete!',
            'result': {
                'toc': toc_data,
                'chapters': chapters,
                'generated_chapters': req.chapters_to_generate
            }
        })
        
    except Exception as e:
        progress_store[job_id].update({
            'status': 'failed',
            'step': 'error',
            'message': f'Generation failed: {str(e)}',
            'error': str(e)
        })