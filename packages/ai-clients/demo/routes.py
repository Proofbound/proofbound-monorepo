"""
Demo interface routes for testing and partner demonstrations.
"""

import json
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from .presets import DEMO_PRESETS

# API base URL for demo interface (different for local vs deployed)
API_BASE_URL = os.getenv("API_BASE_URL", "")

router = APIRouter()


@router.get("/demo", response_class=HTMLResponse)
def demo_interface(request: Request):
    """Demo interface with presets for testing and partner demonstrations."""
    # Detect deployment environment - default to deployed unless we detect localhost
    host = request.headers.get("host", "")
    x_forwarded_host = request.headers.get("x-forwarded-host", "")
    x_forwarded_for = request.headers.get("x-forwarded-for", "")
    
    # Only use relative URLs if we detect localhost (local development)
    if "localhost" in host or "127.0.0.1:8000" in host:
        # For local development, use relative URLs (empty base_url)
        base_url = ""
    else:
        # Default: assume deployed - hardcode the HAL9 deployment URL
        base_url = "https://api.hal9.com/books/bookgeneratorapi/proxy"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI Book Generator - Demo Interface</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            h2 {{ color: #444; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
            .preset-section, .endpoint-section {{ margin: 30px 0; }}
            select, button, input, textarea {{ padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ background: #007acc; color: white; cursor: pointer; font-weight: bold; }}
            button:hover {{ background: #005a9e; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
            input, textarea {{ width: 100%; max-width: 500px; }}
            textarea {{ height: 100px; }}
            .response {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 15px 0; border-radius: 4px; white-space: pre-wrap; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; }}
            .timing {{ color: #28a745; font-weight: bold; }}
            .error {{ color: #dc3545; }}
            .endpoint-test {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #007acc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Book Generator - Demo Interface</h1>
            <p style="text-align: center; color: #666;">Testing interface with real AI calls for partner demonstrations</p>
            <p style="text-align: center; font-size: 12px; color: #999;">
                Base URL: "{base_url}" ({"local development" if not base_url else "deployed"})
                <br>Host: "{host}" | X-Forwarded-Host: "{x_forwarded_host}" | X-Forwarded-For: "{x_forwarded_for}"
            </p>
            
            <div class="preset-section">
                <h2>Demo Presets</h2>
                <label for="presetSelect">Choose a preset example:</label>
                <select id="presetSelect" onchange="loadPreset()">
                    <option value="">-- Select Preset --</option>
                    <option value="eyes_health">Eyes on Health (AI + Healthcare)</option>
                    <option value="microbiome">The Microbiome Revolution (Science)</option>
                    <option value="novel_test">The Silicon Valley Heist (Fiction)</option>
                </select>
                
                <div style="margin-top: 20px;">
                    <label for="mockMode">
                        <input type="checkbox" id="mockMode" onchange="toggleMockMode()"> 
                        🚀 <strong>Mock Mode</strong> - Use fast mock responses (no AI costs)
                    </label>
                    <p style="font-size: 12px; color: #666; margin: 5px 0;">
                        Toggle to test API responses without expensive AI calls. Perfect for development and demo preparation.<br>
                        📄 <em>Note: PDF/Cover generation in mock mode returns a sample PDF file.</em>
                    </p>
                </div>
            </div>

            <div class="form-group">
                <label for="title">Book Title:</label>
                <input type="text" id="title" placeholder="Enter book title">
            </div>
            <div class="form-group">
                <label for="author">Author:</label>
                <input type="text" id="author" placeholder="Enter author name">
            </div>
            <div class="form-group">
                <label for="bookIdea">Book Idea:</label>
                <textarea id="bookIdea" placeholder="Describe your book concept"></textarea>
            </div>

            <div class="endpoint-test">
                <h2>1. Generate Table of Contents</h2>
                <button onclick="testTOC()">🔍 Generate TOC</button>
                <div id="tocResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>2a. Generate Book Draft (Legacy)</h2>
                <button onclick="testDraft()" id="draftBtn">📝 Generate Draft (monolithic)</button>
                <div id="draftResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>2b. Generate Book Chapter-by-Chapter</h2>
                <div class="form-group">
                    <label for="parallelGeneration">
                        <input type="checkbox" id="parallelGeneration"> 
                        Parallel Generation (faster, no cross-chapter context)
                    </label>
                </div>
                <div class="form-group">
                    <label for="maxConcurrent">Max Concurrent Chapters:</label>
                    <input type="number" id="maxConcurrent" value="3" min="1" max="10">
                </div>
                <button onclick="testChapterByChapter()">📚 Generate Book (chapter-by-chapter)</button>
                <div id="chapterBookResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>2c. Generate Single Chapter</h2>
                <div class="form-group">
                    <label for="chapterNumber">Chapter Number:</label>
                    <input type="number" id="chapterNumber" value="1" min="1">
                </div>
                <div class="form-group">
                    <label for="chapterName">Chapter Name:</label>
                    <input type="text" id="chapterName" placeholder="Enter chapter name">
                </div>
                <div class="form-group">
                    <label for="chapterIdeas">Chapter Ideas (one per line):</label>
                    <textarea id="chapterIdeas" placeholder="Enter key ideas for this chapter, one per line"></textarea>
                </div>
                <button onclick="testSingleChapter()">📄 Generate Single Chapter</button>
                <div id="singleChapterResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>2d. Generate TOC + Selected Chapters (NEW)</h2>
                <p style="color: #666; font-style: italic;">Stateless endpoint that generates TOC internally and then creates selected chapters in one call.</p>
                <div class="form-group">
                    <label for="chaptersToGenerate">Chapters to Generate (comma-separated):</label>
                    <input type="text" id="chaptersToGenerate" value="1" placeholder="e.g., 1,2,3">
                </div>
                <button onclick="testBookChapters()">🔄 Generate TOC + Chapters</button>
                <div id="bookChaptersResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>3. Generate PDF</h2>
                <button onclick="testPDF()" id="pdfBtn">📄 Generate PDF (uses draft from above)</button>
                <div id="pdfResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>4. Generate Cover</h2>
                <div class="form-group">
                    <label for="numPages">Number of Pages:</label>
                    <input type="number" id="numPages" value="200" min="1">
                </div>
                <button onclick="testCover()">🎨 Generate Cover</button>
                <div id="coverResponse" class="response" style="display:none;"></div>
            </div>
        </div>

        <script>
            const presets = {json.dumps(DEMO_PRESETS)};
            const baseURL = "{base_url}";
            let currentTOC = null;
            let currentMarkdown = null;
            let mockModeEnabled = false;
            
            function loadPreset() {{
                const selectedPreset = document.getElementById('presetSelect').value;
                if (selectedPreset && presets[selectedPreset]) {{
                    document.getElementById('title').value = presets[selectedPreset].title;
                    document.getElementById('author').value = presets[selectedPreset].author;
                    document.getElementById('bookIdea').value = presets[selectedPreset].book_idea;
                }}
            }}
            
            function toggleMockMode() {{
                mockModeEnabled = document.getElementById('mockMode').checked;
                const statusText = document.querySelector('.container p');
                if (mockModeEnabled) {{
                    statusText.textContent = 'Testing interface with MOCK responses (no AI costs) 🚀';
                    statusText.style.color = '#28a745';
                }} else {{
                    statusText.textContent = 'Testing interface with real AI calls for partner demonstrations';
                    statusText.style.color = '#666';
                }}
            }}
            
            function getEndpointURL(endpoint) {{
                if (mockModeEnabled) {{
                    return baseURL ? `${{baseURL}}/mock${{endpoint}}` : `/mock${{endpoint}}`;
                }} else {{
                    return baseURL ? `${{baseURL}}${{endpoint}}` : `${{endpoint}}`;
                }}
            }}

            function getFormData() {{
                return {{
                    title: document.getElementById('title').value,
                    author: document.getElementById('author').value,
                    book_idea: document.getElementById('bookIdea').value
                }};
            }}

            function showResponse(elementId, data, timing) {{
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                const timingText = timing ? `\\n\\n⏱️ Completed in ${{timing.toFixed(2)}}s` : '';
                element.innerHTML = `<div class="timing">Response:</div>${{JSON.stringify(data, null, 2)}}${{timingText}}`;
            }}

            function showError(elementId, error) {{
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                element.innerHTML = `<div class="error">❌ Error: ${{error}}</div>`;
            }}

            async function testTOC() {{
                const formData = getFormData();
                if (!formData.title || !formData.author || !formData.book_idea) {{
                    alert('Please fill in title, author, and book idea');
                    return;
                }}
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/toc'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(formData)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        currentTOC = data;
                        showResponse('tocResponse', data, timing);
                    }} else {{
                        showError('tocResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('tocResponse', error.message);
                }}
            }}

            async function testDraft() {{
                if (!currentTOC) {{
                    alert('Please generate TOC first');
                    return;
                }}
                
                const formData = getFormData();
                const payload = {{ ...formData, toc: currentTOC }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/draft'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        currentMarkdown = data.markdown;
                        const preview = data.markdown.substring(0, 500) + '...';
                        showResponse('draftResponse', {{...data, markdown: preview}}, timing);
                    }} else {{
                        showError('draftResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('draftResponse', error.message);
                }}
            }}

            async function testPDF() {{
                if (!currentTOC || !currentMarkdown) {{
                    alert('Please generate TOC and draft first');
                    return;
                }}
                
                const formData = getFormData();
                const payload = {{ ...formData, toc: currentTOC, markdown: currentMarkdown }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/pdf'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${{formData.title.replace(/[^a-zA-Z0-9]/g, '_')}}.pdf`;
                        a.click();
                        showResponse('pdfResponse', {{message: 'PDF generated and downloaded', size: `${{blob.size}} bytes`}}, timing);
                    }} else {{
                        const errorData = await response.json();
                        showError('pdfResponse', errorData.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('pdfResponse', error.message);
                }}
            }}

            async function testCover() {{
                const formData = getFormData();
                const numPages = parseInt(document.getElementById('numPages').value);
                if (!formData.title || !formData.author || !formData.book_idea) {{
                    alert('Please fill in title, author, and book idea');
                    return;
                }}
                
                const payload = {{ ...formData, num_pages: numPages }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/cover'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${{formData.title.replace(/[^a-zA-Z0-9]/g, '_')}}_cover.pdf`;
                        a.click();
                        showResponse('coverResponse', {{message: 'Cover generated and downloaded', size: `${{blob.size}} bytes`}}, timing);
                    }} else {{
                        const errorData = await response.json();
                        showError('coverResponse', errorData.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('coverResponse', error.message);
                }}
            }}

            async function testChapterByChapter() {{
                if (!currentTOC) {{
                    alert('Please generate TOC first');
                    return;
                }}
                
                const formData = getFormData();
                const parallel = document.getElementById('parallelGeneration').checked;
                const maxConcurrent = parseInt(document.getElementById('maxConcurrent').value);
                
                const payload = {{
                    book_context: {{
                        title: formData.title,
                        author: formData.author,
                        book_idea: formData.book_idea
                    }},
                    toc: currentTOC,
                    parallel_generation: parallel,
                    max_concurrent_chapters: maxConcurrent
                }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/generate-book'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        // Store for PDF generation
                        currentMarkdown = data.chapters.map(ch => `## ${{ch.section_name}}\\n\\n${{ch.content}}`).join('\\n\\n');
                        
                        // Show summary with stats
                        const summary = {{
                            total_chapters: data.chapters.length,
                            total_words: data.total_word_count,
                            generation_method: data.generation_summary.generation_method,
                            average_words_per_chapter: data.generation_summary.average_words_per_chapter,
                            cost_estimate: data.total_cost_estimate,
                            chapters_preview: data.chapters.slice(0, 2).map(ch => ({{
                                chapter: ch.chapter_number,
                                title: ch.section_name,
                                words: ch.word_count,
                                content_preview: ch.content.substring(0, 200) + '...'
                            }}))
                        }};
                        
                        showResponse('chapterBookResponse', summary, timing);
                    }} else {{
                        showError('chapterBookResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('chapterBookResponse', error.message);
                }}
            }}

            async function testSingleChapter() {{
                const formData = getFormData();
                const chapterNumber = parseInt(document.getElementById('chapterNumber').value);
                const chapterName = document.getElementById('chapterName').value;
                const chapterIdeas = document.getElementById('chapterIdeas').value.split('\\n').filter(idea => idea.trim());
                
                if (!formData.title || !formData.author || !formData.book_idea || !chapterName || chapterIdeas.length === 0) {{
                    alert('Please fill in all fields including chapter name and ideas');
                    return;
                }}
                
                const payload = {{
                    chapter_outline: {{
                        chapter_number: chapterNumber,
                        section_name: chapterName,
                        section_ideas: chapterIdeas
                    }},
                    book_context: {{
                        title: formData.title,
                        author: formData.author,
                        book_idea: formData.book_idea
                    }}
                }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/generate-chapter'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        const preview = {{
                            chapter_number: data.chapter_number,
                            section_name: data.section_name,
                            word_count: data.word_count,
                            generation_time: data.generation_time,
                            cost_estimate: data.cost_estimate,
                            content_preview: data.content.substring(0, 500) + '...'
                        }};
                        showResponse('singleChapterResponse', preview, timing);
                    }} else {{
                        showError('singleChapterResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('singleChapterResponse', error.message);
                }}
            }}

            async function testBookChapters() {{
                const formData = getFormData();
                const chaptersToGenerateInput = document.getElementById('chaptersToGenerate').value;
                
                if (!formData.title || !formData.author || !formData.book_idea) {{
                    alert('Please fill in title, author, and book idea');
                    return;
                }}
                
                // Parse chapters to generate
                const chaptersToGenerate = chaptersToGenerateInput.split(',').map(ch => parseInt(ch.trim())).filter(ch => !isNaN(ch));
                if (chaptersToGenerate.length === 0) {{
                    alert('Please specify at least one chapter number');
                    return;
                }}
                
                const payload = {{
                    title: formData.title,
                    author: formData.author,
                    book_idea: formData.book_idea,
                    chapters_to_generate: chaptersToGenerate
                }};
                
                const startTime = Date.now();
                try {{
                    const response = await fetch(getEndpointURL('/generate-book-chapters'), {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(payload)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        // Store TOC and markdown for potential PDF generation
                        currentTOC = data.toc;
                        currentMarkdown = data.chapters.map(ch => `## ${{ch.section_name}}\\n\\n${{ch.content}}`).join('\\n\\n');
                        
                        // Show summary with stats
                        const summary = {{
                            generated_chapters: data.generated_chapters,
                            toc_sections: data.toc.length,
                            total_cost: data.total_estimated_cost,
                            generation_time: data.total_generation_time,
                            metadata: data.metadata,
                            chapters_preview: data.chapters.map(ch => ({{
                                chapter_number: ch.chapter_number,
                                section_name: ch.section_name,
                                word_count: ch.word_count,
                                cost_estimate: ch.cost_estimate,
                                content_preview: ch.content.substring(0, 300) + '...'
                            }}))
                        }};
                        
                        showResponse('bookChaptersResponse', summary, timing);
                    }} else {{
                        showError('bookChaptersResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('bookChaptersResponse', error.message);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_content


@router.get("/demo/presets")
def get_demo_presets():
    """Return available demo presets."""
    return DEMO_PRESETS