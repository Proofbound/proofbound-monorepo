"""
Example of Server-Sent Events for progress tracking.
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import time
import asyncio

@app.post("/generate-book-chapters-stream")
async def generate_book_chapters_stream(req: BookChaptersRequest):
    """Generate TOC + chapters with real-time progress updates via SSE."""
    
    async def generate_with_progress():
        try:
            # Step 1: Generate TOC
            yield f"data: {json.dumps({'step': 'toc', 'status': 'starting', 'message': 'Generating table of contents...'})}\n\n"
            
            # Simulate TOC generation
            await asyncio.sleep(1)  # Replace with actual ask_llm call
            toc_data = [{"section_name": "Chapter 1", "section_ideas": ["idea1", "idea2"]}]
            
            yield f"data: {json.dumps({'step': 'toc', 'status': 'complete', 'data': toc_data})}\n\n"
            
            # Step 2: Generate chapters
            total_chapters = len(req.chapters_to_generate)
            for i, chapter_num in enumerate(req.chapters_to_generate):
                progress = (i + 1) / total_chapters * 100
                
                yield f"data: {json.dumps({
                    'step': 'chapter',
                    'status': 'progress',
                    'chapter_number': chapter_num,
                    'progress': progress,
                    'message': f'Generating chapter {chapter_num}...'
                })}\n\n"
                
                # Simulate chapter generation
                await asyncio.sleep(2)  # Replace with actual chapter generation
                
                chapter_data = {
                    'chapter_number': chapter_num,
                    'content': f'Generated content for chapter {chapter_num}...',
                    'word_count': 500
                }
                
                yield f"data: {json.dumps({
                    'step': 'chapter',
                    'status': 'complete',
                    'chapter_number': chapter_num,
                    'data': chapter_data
                })}\n\n"
            
            # Final completion
            yield f"data: {json.dumps({'step': 'complete', 'status': 'done', 'message': 'All chapters generated!'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'status': 'failed', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_with_progress(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )