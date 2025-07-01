import os
import json
import time
from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI

# Environment configuration
OAI_TOKEN = os.getenv("HAL9_TOKEN")
if not OAI_TOKEN:
    raise RuntimeError("HAL9_TOKEN must be set")

# API base URL for demo interface (different for local vs deployed)
API_BASE_URL = os.getenv("API_BASE_URL", "")  # Default to relative URLs for local development

openai_client = OpenAI(
    base_url="https://api.hal9.com/proxy/server=https://api.openai.com/v1/",
    api_key=OAI_TOKEN,
)

# Demo presets
DEMO_PRESETS = {
    "eyes_health": {
        "title": "Eyes on Health",
        "author": "Richard Sprague",
        "book_idea": "AI-powered retinal imaging for wellness assessment. How artificial intelligence can revolutionize preventive healthcare by analyzing retinal photographs."
    },
    "microbiome": {
        "title": "The Microbiome Revolution",
        "author": "Dr. Sarah Chen",
        "book_idea": "Personal microbiome optimization strategies. A comprehensive guide to understanding and improving your gut health through diet, lifestyle, and modern science."
    },
    "novel_test": {
        "title": "The Silicon Valley Heist",
        "author": "Alex Morgan",
        "book_idea": "Tech thriller about AI startup corporate espionage. A fast-paced novel exploring the dark side of Silicon Valley's competitive landscape."
    }
}

# Pydantic models
class Section(BaseModel):
    section_name: str
    section_ideas: List[str] = Field(..., description="List of bullet-point ideas")

class TOCRequest(BaseModel):
    title: str
    author: str
    book_idea: str

# Helper function
def ask_llm(prompt: str, default: str = "") -> str:
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return resp.choices[0].message.content or default
    except Exception:
        return default

# FastAPI app
app = FastAPI(
    title="AI-Powered Book Generator (Simple)",
    description="Generate TOC via REST API.",
)

@app.get("/test")
def test_endpoint():
    return {
        "message": "Simple API is up and running!",
        "available_endpoints": ["/toc", "/demo", "/demo/presets"],
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

@app.get("/demo", response_class=HTMLResponse)
def demo_interface():
    """Demo interface with presets for testing TOC generation."""
    # Auto-detect deployment environment since HAL9 doesn't support --env flag
    if API_BASE_URL:
        base_url = API_BASE_URL
    elif os.getenv("HAL9_TOKEN") and not os.getenv("API_BASE_URL"):
        # We're deployed (HAL9_TOKEN exists) but no explicit API_BASE_URL set
        # This indicates we're running on HAL9 deployed environment
        base_url = "https://api.hal9.com/books/bookgeneratorapi/proxy"
    else:
        # Local development
        base_url = ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI Book Generator - Demo Interface (TOC Only)</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            h2 {{ color: #444; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
            .preset-section {{ margin: 30px 0; }}
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
            .note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 4px; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Book Generator - Demo Interface</h1>
            <p style="text-align: center; color: #666;">Simple version - TOC generation only (no system dependencies required)</p>
            
            <div class="note">
                <strong>Note:</strong> This is the lightweight version that generates table of contents only. 
                For full PDF/cover generation, use the full version with WeasyPrint dependencies.
            </div>
            
            <div class="preset-section">
                <h2>Demo Presets</h2>
                <label for="presetSelect">Choose a preset example:</label>
                <select id="presetSelect" onchange="loadPreset()">
                    <option value="">-- Select Preset --</option>
                    <option value="eyes_health">Eyes on Health (AI + Healthcare)</option>
                    <option value="microbiome">The Microbiome Revolution (Science)</option>
                    <option value="novel_test">The Silicon Valley Heist (Fiction)</option>
                </select>
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
                <h2>Generate Table of Contents</h2>
                <p>Test the TOC generation endpoint with real AI calls</p>
                <button onclick="testTOC()">🔍 Generate TOC</button>
                <div id="tocResponse" class="response" style="display:none;"></div>
            </div>
        </div>

        <script>
            const presets = {json.dumps(DEMO_PRESETS)};
            const baseURL = typeof API_BASE_URL !== 'undefined' && API_BASE_URL !== '' ? API_BASE_URL : "{base_url}";
            
            function loadPreset() {{
                const selectedPreset = document.getElementById('presetSelect').value;
                if (selectedPreset && presets[selectedPreset]) {{
                    document.getElementById('title').value = presets[selectedPreset].title;
                    document.getElementById('author').value = presets[selectedPreset].author;
                    document.getElementById('bookIdea').value = presets[selectedPreset].book_idea;
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
                    const response = await fetch(`${{baseURL}}/toc`, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(formData)
                    }});
                    const data = await response.json();
                    const timing = (Date.now() - startTime) / 1000;
                    
                    if (response.ok) {{
                        showResponse('tocResponse', data, timing);
                    }} else {{
                        showError('tocResponse', data.detail || 'Unknown error');
                    }}
                }} catch (error) {{
                    showError('tocResponse', error.message);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/demo/presets")
def get_demo_presets():
    """Return available demo presets."""
    return DEMO_PRESETS