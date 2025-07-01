import os
import json
import base64
import time
import requests
from io import BytesIO
from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from openai import OpenAI
from replicate.client import Client as ReplicateClient
from PIL import Image, ImageEnhance, ImageFilter
from weasyprint import HTML
import pypandoc
from bs4 import BeautifulSoup



# ——————————————————————————————————————————————————————————————————
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

replicate_client = ReplicateClient(
    base_url="https://api.hal9.com/proxy/server=https://api.replicate.com",
    api_token=OAI_TOKEN,
)

# Ensure Pandoc is installed for markdown → HTML conversion
try:
    pypandoc.get_pandoc_version()
except OSError:
    pypandoc.download_pandoc()


# ——————————————————————————————————————————————————————————————————
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

# Performance tracking decorator
def track_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        if hasattr(result, '__dict__'):
            result.__dict__['_timing'] = duration
        return result
    return wrapper

# ——————————————————————————————————————————————————————————————————
# Pydantic models

class Section(BaseModel):
    section_name: str
    section_ideas: List[str] = Field(..., description="List of bullet-point ideas")

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


# ——————————————————————————————————————————————————————————————————
# Helpers

def ask_llm(prompt: str, default: str = "") -> str:
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return resp.choices[0].message.content
    except Exception:
        return default
    
def markdown_to_html(md: str) -> str:
    return pypandoc.convert_text(md, 'html', format='md')

def _ensure_image(src) -> Image.Image:
    if isinstance(src, Image.Image):
        return src
    if isinstance(src, (bytes, bytearray)):
        return Image.open(BytesIO(src))
    if hasattr(src, "read"):
        return Image.open(src)
    return Image.open(src)

def inches_to_px(inches: float, dpi: int = 300) -> int:
    return int(inches * dpi)

def create_cover_image(front_img, back_img, spine_color, num_pages, paper_thickness, dpi, back_brightness=0.2, back_blur=2.0):

    # Dimensions in inches
    front_w_in, h_in = 6.125, 9.25
    back_w_in = front_w_in
    spine_w_in = num_pages * paper_thickness
    full_w_in = back_w_in + spine_w_in + front_w_in

    # Pixels
    full_w_px = inches_to_px(full_w_in, dpi)
    h_px = inches_to_px(h_in, dpi)
    back_w_px = inches_to_px(back_w_in, dpi)
    spine_w_px = inches_to_px(spine_w_in, dpi)
    front_w_px = inches_to_px(front_w_in, dpi)

    canvas = Image.new("RGB", (full_w_px, h_px), "white")
    # Spine
    spine_rect = Image.new("RGB", (spine_w_px, h_px), spine_color)
    canvas.paste(spine_rect, (back_w_px, 0))

    # Back
    if back_img:
        back = _ensure_image(back_img).convert("RGB").resize((back_w_px, h_px))
        back = ImageEnhance.Brightness(back).enhance(back_brightness)
        if back_blur > 0:
            back = back.filter(ImageFilter.GaussianBlur(back_blur))
        canvas.paste(back, (0, 0))

    # Front
    if front_img:
        front = _ensure_image(front_img).convert("RGB").resize((front_w_px, h_px))
        canvas.paste(front, (back_w_px + spine_w_px, 0))

    return canvas, (full_w_in, h_in, back_w_in, spine_w_in, front_w_in)



def image_bytes_to_base64(img_bytes: bytes) -> str:
    """Take raw image bytes, return a base64‐data URI string."""
    img = Image.open(BytesIO(img_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def generate_pdf_from_html(html: str) -> bytes:
    buf = BytesIO()
    HTML(string=html).write_pdf(buf)
    return buf.getvalue()





# ——————————————————————————————————————————————————————————————————
# FastAPI app

app = FastAPI(
    title="AI-Powered Book Generator",
    description="Convert book ideas → TOC, draft, PDF, and cover via REST.",
)

@app.get("/test")
def test_endpoint():
    """
    Simple test endpoint to verify the service is running.
    """
    return {
        "message": "API is up and running!!!",
        "available_endpoints": ["/toc", "/draft", "/pdf", "/cover", "/demo", "/demo/presets"]
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

@app.post("/draft")
def generate_draft(req: DraftRequest):
    """Take a TOC + metadata, return a single Markdown string draft."""
    md = []
    total = sum(len(sec.section_ideas) for sec in req.toc)
    count = 0

    for sec in req.toc:
        md.append(f"## {sec.section_name}\n")
        for idea in sec.section_ideas:
            count += 1
            prompt = (
                f"Act as an expert writer of the book '{req.title}' about '{req.book_idea}'. "
                f"Expand on '{idea}' in chapter '{sec.section_name}'. Write a couple of pages. "
                "Reply only with the contents of the section. Do not add chapter numbers or chapter titles."
            )
            content = ask_llm(prompt, default=f"*Error generating {idea}*")
            md.append(content + "\n\n")

    return {"markdown": "".join(md)}

@app.post("/pdf")
def generate_book_pdf(req: PDFRequest):
    """Convert Markdown + TOC + metadata → formatted PDF bytes."""
    # 1) Markdown → HTML
    html_body = markdown_to_html(req.markdown)
    # 2) Inject IDs for TOC
    soup = BeautifulSoup(html_body, "html.parser")
    for i, h2 in enumerate(soup.find_all("h2"), start=1):
        h2["id"] = f"sec{i}"
    body = str(soup)

    # 3) Build TOC HTML/CSS
    toc_items = []
    for i, sec in enumerate(req.toc, start=1):
        toc_items.append(
            f"<li><span class='toc-label'>{sec.section_name}</span>"
            f"<span class='pagenum'></span></li>"
        )
    toc_html = "<div class='toc'><h1>Table of Contents</h1><ol>" + "".join(toc_items) + "</ol></div>"
    toc_css = "\n".join(
        f".toc ol li:nth-child({i}) .pagenum:after {{content: leader(\".\") target-counter(\"#sec{i}\", page);}}"
        for i in range(1, len(req.toc) + 1)
    )

    # 4) Full HTML template 
    full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                /*--- Define named pages ---*/
                @page titlepage {{
                  size: 6in 9in;
                  margin: 0;
                  @top-center {{ content: none; }}
                  @bottom-center {{ content: none; }}
                }}
                @page blank {{
                  size: 6in 9in;
                  margin: 0;
                  @top-center {{ content: none; }}
                  @bottom-center {{ content: none; }}
                }}
                @page toc {{
                  size: 6in 9in;
                  margin: 1in;
                  @top-center {{ content: none; }}
                  @bottom-center {{ content: "Page " counter(page); }}
                }}
                /* default content pages */
                @page {{
                  size: 6in 9in;
                  margin: 1in;
                  @top-center {{
                    content: "{req.title}";
                    font-size: 8pt;
                    font-family: Georgia, serif;
                  }}
                  @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 8pt;
                    font-family: Georgia, serif;
                  }}
                }}

                html, body {{ margin:0; padding:0; }}
                /*--- Title Page ---*/
                .titlepage {{
                  page: titlepage;
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  flex-direction: column;
                  height: 9in;
                  page-break-after: always;
                }}

                .titlepage h1 {{
                    display: inline-block;
                    text-align: center;
                    overflow-wrap: break-word;
                    max-width: 90%;
                    font-family: Georgia, serif; font-size:24pt; margin:0;
                    margin: 0;
                }}
                .titlepage h2 {{
                    display: inline-block;
                    text-align: center;
                    overflow-wrap: break-word;
                    max-width: 90%;
                    font-family: Georgia, serif; font-size:14pt; margin-top: 1em;
                    margin: 0;
                }}

                /*--- Blank pages (2 & 4) ---*/
                .blank {{
                  page: blank;
                  page-break-after: always;
                }}

                /*--- TOC page (3) ---*/
                .toc {{
                  page: toc;
                  page-break-after: always;
                  font-family:Georgia, serif;
                  font-size:10pt;
                }}
                .toc h1 {{ text-align:center; margin-bottom:1em; }}
                .toc ol {{
                  list-style:none;
                  counter-reset: item;
                  padding:0;
                }}
                .toc li {{
                counter-increment: item;
                margin-bottom: 0.5em;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                flex-wrap: wrap;
                }}
                .toc-label {{
                flex: 1 1 auto;
                padding-right: 1em;
                word-wrap: break-word;
                max-width: 80%;
                }}
                .toc-label::before {{
                  content: counter(item) ". ";
                }}
                .pagenum {{ /* filled via CSS below */ }}
                {toc_css}

                /*--- Actual book content starts on page 5 ---*/
                .content {{
                  font-family:Georgia, serif;
                  font-size:10pt;
                  line-height:1.3;
                  text-align:justify;
                }}
                .content h2 {{
                  page-break-before: always;
                  text-align: center;
                }}
              </style>
            </head>
            <body>
              <!-- Page 1: Title -->
              <div class="titlepage">
                <h1>{req.title}</h1>
                <h2>{req.author}</h2>
              </div>

              <!-- Page 2: blank -->
              <div class="blank"></div>

              <!-- Page 3: TOC -->
              {toc_html}

              <!-- Page 4: blank -->
              <div class="blank"></div>

              <!-- Page 5+: content -->
              <div class="content">
                {body}
              </div>
            </body>
            </html>
            """

    try:
        pdf_bytes = HTML(string=full_html).write_pdf()
    except Exception as e:
        raise HTTPException(500, detail=f"PDF generation failed: {str(e)}")
    return Response(content=pdf_bytes, media_type="application/pdf")

@app.post("/cover")
def generate_cover(req: CoverRequest):
    """Generate a full 6x9 cover PDF (front/back/spine) via AI + assemble."""
    # 1) Generate a front image via OpenAI Images
    front_prompt = (
        f"Generate a book cover (6×9 in) for a book titles '{req.title}' by the author {req.author} "
        f"about '{req.book_idea}'. Do not put any margins as this cover might be cropped. Be very creative. The only texts in the cover should be the book title and the book author name."
    )
    img_resp = openai_client.images.generate(model="gpt-image-1", prompt=front_prompt)
    front_b64 = img_resp.data[0].b64_json
    front_bytes = base64.b64decode(front_b64)

    # 2) Generate a back illustration prompt via LLM + Replicate
    back_desc = ask_llm(f"Write a vivid, text‐free illustration description around the idea of '{req.book_idea}'.")
    replicate_out = replicate_client.run(
        "black-forest-labs/flux-dev",
        input={"prompt": back_desc, "aspect_ratio": "2:3"}
    )
    back_url = replicate_out[0]
    back_img = requests.get(back_url).content

    canvas_img, (full_w_in, h_in, back_w_in, spine_w_in, front_w_in) = create_cover_image(
        front_bytes,
        back_img,
        spine_color="#000000",
        back_brightness=0.2,
        back_blur=2.0,
        num_pages=req.num_pages,
        paper_thickness=0.00225,
        dpi=300,
    )

    # 4) Back‐cover text
    back_blurb = ask_llm(
        f"Write the text for the back cover of the book '{req.title}' "
        f"by the author '{req.author}' that is about '{req.book_idea}'. REPLY ONLY WITH THE BACK COVER TEXT."
    ) or ""
    back_desc_paragraphs = "".join(f"<p>{line}</p>" for line in back_blurb.split("\n"))

    # 5) Encode assembled canvas to base64
    buf = BytesIO()
    canvas_img.save(buf, format="PNG")
    bg_b64 = base64.b64encode(buf.getvalue()).decode()

    # 6) Conditionally include spine text
    spine_html = (
        f"<div class='spine-text'>{req.title}</div>"
        if req.include_spine_title else ""
    )

    # 7) Full HTML/CSS from your Streamlit app
    html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset='utf-8'>
        <style>
          @font-face {{
            font-family: "MyCustomFont";
            src: url("fonts/Kanit-Bold.ttf") format("truetype");
          }}
          @page {{ size:{full_w_in:.3f}in {h_in:.2f}in; margin:0 }}
          body {{ margin:0; padding:0 }}
          .cover {{ position:relative; width:{full_w_in:.3f}in; height:{h_in:.2f}in; }}
          .cover img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
          .front-text {{
            position:absolute;
            left:{(back_w_in+spine_w_in):.3f}in;
            top:0.5in;
            width:{front_w_in:.3f}in;
            text-align:center;
            font-size:48pt;
            font-family:MyCustomFont;
            color:white; stroke:black; stroke-width:2;
          }}
          .author-text {{
            position:absolute;
            left:{(back_w_in+spine_w_in):.3f}in;
            top:1.5in;
            width:{front_w_in:.3f}in;
            text-align:center;
            font-size:24pt;
            font-family:MyCustomFont;
            color:white; stroke:black; stroke-width:2;
          }}
          .spine-text {{
            position:absolute;
            top:50%; left:{(back_w_in + spine_w_in/2):.3f}in;
            transform:translate(-50%,-50%) rotate(90deg);
            transform-origin:center;
            font-size:10pt;
            font-family:MyCustomFont;
            color:white;
            white-space:nowrap;
          }}
          .back-text {{
            position:absolute;
            left:0; top:0.5in;
            width:{(back_w_in - 1 - spine_w_in/2):.3f}in;
            padding:0.6in;
            font-size:12pt;
            font-family:MyCustomFont;
            color:white;
          }}
          .back-text p {{
            text-indent:2em;
            margin:0 0 1em 0;
          }}
        </style>
      </head>
      <body>
        <div class='cover'>
          <img src='data:image/png;base64,{bg_b64}' />
          {spine_html}
          <div class="back-text" style="text-align: justify;">
            {back_desc_paragraphs}
          </div>
        </div>
      </body>
    </html>
    """

    # 8) Render PDF
    pdf_buf = BytesIO()
    HTML(string=html).write_pdf(pdf_buf)
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(content=pdf_buf.getvalue(), headers=headers, media_type="application/pdf")

@app.get("/demo", response_class=HTMLResponse)
def demo_interface():
    """Demo interface with presets for testing and partner demonstrations."""
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
                <h2>1. Generate Table of Contents</h2>
                <button onclick="testTOC()">🔍 Generate TOC</button>
                <div id="tocResponse" class="response" style="display:none;"></div>
            </div>

            <div class="endpoint-test">
                <h2>2. Generate Book Draft</h2>
                <button onclick="testDraft()" id="draftBtn">📝 Generate Draft (uses TOC from above)</button>
                <div id="draftResponse" class="response" style="display:none;"></div>
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
            const baseURL = API_BASE_URL !== undefined ? API_BASE_URL : base_url;
            let currentTOC = null;
            let currentMarkdown = null;
            
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
                    const response = await fetch(`${{baseURL}}/draft`, {{
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
                    const response = await fetch(`${{baseURL}}/pdf`, {{
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
                    const response = await fetch(`${{baseURL}}/cover`, {{
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
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/demo/presets")
def get_demo_presets():
    """Return available demo presets."""
    return DEMO_PRESETS
