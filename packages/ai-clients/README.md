# AI-Powered Book Generator API

A modular FastAPI application that generates books chapter-by-chapter using AI services. Features table of contents generation, flexible chapter creation, PDF formatting, and AI-generated covers through HAL9 proxy.

## Features

- **TOC Generation**: Generate structured table of contents from book ideas
- **Chapter-by-Chapter Generation**: Create individual chapters or selected chapters with context awareness
- **Composite Generation**: Generate TOC + selected chapters in one stateless call
- **Draft Creation**: Full book content generation with multiple strategies
- **PDF Generation**: Create formatted PDFs with proper book layout  
- **Cover Generation**: AI-generated book covers with front/back/spine design
- **Interactive Demo**: Built-in testing interface with preset examples
- **🚀 Mock API System**: Cost-free testing with realistic responses (no AI calls required)

## Quick Start

### Prerequisites

**For Mock Mode (Recommended for development):**
- Python 3.10+
- No other dependencies required

**For Production Mode with AI:**
- Python 3.10+
- HAL9_TOKEN environment variable
- System dependencies for PDF generation (see Installation)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd bookgeneratorapi
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies (macOS):**
   ```bash
   brew install python-tk pango gdk-pixbuf libffi gobject-introspection cairo gtk+3
   ```

4. **Set environment variable:**
   ```bash
   export HAL9_TOKEN=your_hal9_token_here
   ```

### Running the Server

**Main version (modular architecture with chapter-by-chapter generation):**
```bash
# If WeasyPrint fails to load, set these environment variables first:
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

uvicorn app:app --reload --port 8000 --host 0.0.0.0
```

**Simple version (TOC only, no system dependencies):**
```bash
uvicorn simple_app:app --reload --port 8000 --host 0.0.0.0
```

## 🚀 Mock Mode Quick Start (No Setup Required)

Perfect for development and testing without AI costs:

1. **Start server:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Visit demo interface:**
   ```
   http://localhost:8000/demo
   ```

3. **Enable mock mode:**
   - Check the "🚀 Mock Mode" checkbox
   - Select a preset (e.g., "Eyes on Health")
   - Test all endpoints instantly without costs

4. **Or call mock API directly:**
   ```bash
   curl -X POST "http://localhost:8000/mock/toc" \
     -H "Content-Type: application/json" \
     -d '{"title": "My Book", "author": "Author", "book_idea": "AI concept"}'
   ```

**Legacy version (original monolithic app, for comparison):**
```bash
uvicorn app_legacy:app --reload --port 8001 --host 0.0.0.0
```

## API Usage

### Production API (With AI)

**Health Check:**
```bash
curl http://localhost:8000/test
```

**Generate Table of Contents:**
```bash
curl -X POST "http://localhost:8000/toc" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Art of AI",
    "author": "John Smith",
    "book_idea": "A comprehensive guide to understanding artificial intelligence"
  }'
```

### 🚀 Mock API (No AI Costs)

**Mock Health Check:**
```bash
curl http://localhost:8000/mock/test
```

**Mock Table of Contents (Instant):**
```bash
curl -X POST "http://localhost:8000/mock/toc" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Art of AI",
    "author": "John Smith",
    "book_idea": "A comprehensive guide to understanding artificial intelligence"
  }'
```

**Mock Chapter Generation (Instant):**
```bash
curl -X POST "http://localhost:8000/mock/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Art of AI",
    "author": "John Smith", 
    "book_idea": "A comprehensive guide to understanding artificial intelligence",
    "chapters_to_generate": [1, 2, 3]
  }'
```

### Generate TOC + Selected Chapters (Production)
```bash
curl -X POST "http://localhost:8000/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Art of AI",
    "author": "John Smith", 
    "book_idea": "A comprehensive guide to understanding artificial intelligence",
    "chapters_to_generate": [1, 2, 3]
  }'
```

### Generate Single Chapter
```bash
curl -X POST "http://localhost:8000/generate-chapter" \
  -H "Content-Type: application/json" \
  -d '{
    "chapter_outline": {
      "chapter_number": 1,
      "section_name": "Introduction to AI",
      "section_ideas": ["What is AI", "History of AI", "Current applications"]
    },
    "book_context": {
      "title": "The Art of AI",
      "author": "John Smith",
      "book_idea": "A comprehensive guide to understanding artificial intelligence"
    }
  }'
```

### Generate Complete Book Chapter-by-Chapter
```bash
curl -X POST "http://localhost:8000/generate-book" \
  -H "Content-Type: application/json" \
  -d '{
    "book_context": {
      "title": "The Art of AI", 
      "author": "John Smith",
      "book_idea": "A comprehensive guide to understanding artificial intelligence"
    },
    "toc": [{"section_name": "Chapter 1", "section_ideas": ["Idea 1", "Idea 2"]}],
    "parallel_generation": false,
    "max_concurrent_chapters": 3
  }'
```

### Generate Draft (legacy monolithic approach)
```bash
curl -X POST "http://localhost:8000/draft" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book Title",
    "author": "Author Name",
    "book_idea": "Book concept",
    "toc": [{"section_name": "Chapter 1", "section_ideas": ["Idea 1", "Idea 2"]}]
  }'
```

### Generate PDF (full version only)
```bash
curl -X POST "http://localhost:8000/pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book Title",
    "author": "Author Name",
    "toc": [...],
    "markdown": "# Chapter 1\n\nContent here..."
  }' --output book.pdf
```

### Generate Cover (full version only)
```bash
curl -X POST "http://localhost:8000/cover" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book Title",
    "author": "Author Name",
    "book_idea": "Book concept",
    "num_pages": 200,
    "include_spine_title": true
  }' --output cover.pdf
```

## Demo Interface

Access the interactive demo at `http://localhost:8000/demo` to test all features with preset examples:

- **Preset Selection**: Choose from healthcare, science, or fiction book examples
- **Real-time Testing**: Test all endpoints with actual AI calls
- **Progress Tracking**: View timing and cost estimates
- **JSON Responses**: See detailed API responses for debugging

## Available Endpoints

### Production Endpoints (Require HAL9_TOKEN)
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/test` | GET | Health check and environment info | JSON status |
| `/toc` | POST | Generate table of contents | JSON array of sections |
| `/draft` | POST | Generate full book draft (legacy) | JSON with markdown |
| `/generate-chapter` | POST | Generate single chapter with context | JSON chapter data |
| `/generate-book` | POST | Generate complete book chapter-by-chapter | JSON with all chapters |
| `/generate-book-chapters` | POST | **NEW**: Generate TOC + selected chapters | JSON with TOC + chapters |
| `/pdf` | POST | Convert markdown to formatted PDF | PDF file download |
| `/cover` | POST | Generate AI book cover | PDF file download |
| `/demo` | GET | Interactive testing interface | HTML demo page |
| `/demo/presets` | GET | Available demo book examples | JSON presets |

### 🚀 Mock Endpoints (No Setup Required)
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/mock/test` | GET | Mock health check | JSON status with mock flag |
| `/mock/toc` | POST | Mock TOC generation (instant) | JSON array of sections |
| `/mock/draft` | POST | Mock full book draft | JSON with markdown |
| `/mock/generate-chapter` | POST | Mock single chapter generation | JSON chapter data |
| `/mock/generate-book` | POST | Mock complete book generation | JSON with all chapters |
| `/mock/generate-book-chapters` | POST | Mock TOC + selected chapters | JSON with TOC + chapters |
| `/mock/pdf` | POST | Mock PDF generation | Sample PDF file download |
| `/mock/cover` | POST | Mock cover generation | Sample PDF file download |

### Key Benefits of Mock Endpoints
- **Zero cost**: No AI API calls or token usage
- **Instant responses**: Sub-second response times
- **Realistic data**: Matches production response schemas exactly
- **External integration**: Perfect for other apps to integrate during development
- **No dependencies**: Works without HAL9_TOKEN or system libraries

## Architecture

### Modular Design
```
bookgeneratorapi/
├── models/                    # Pydantic data models
│   ├── section_model.py       # TOC sections
│   ├── request_models.py      # Legacy API models  
│   └── chapter_models.py      # Chapter-by-chapter models
├── services/                  # Business logic services
│   ├── ai_client.py          # OpenAI/Replicate clients
│   ├── pdf_generator.py      # PDF generation
│   ├── cover_generator.py    # Cover generation
│   └── chapter_generator.py  # Chapter-by-chapter service
├── demo/                     # Interactive demo interface
│   ├── presets.py           # Demo book examples
│   └── routes.py            # Demo UI with mock mode toggle
├── mock_data/                # 🚀 NEW: Mock response system
│   ├── responses.py         # Mock data generation functions
│   └── Eyes_on_Health_cover.pdf  # Sample PDF for downloads
├── tests/                    # Unit tests
├── test_mock_endpoints.py    # 🚀 NEW: Mock endpoint validation
├── app.py                    # Main modular app with mock endpoints
├── app_legacy.py            # Original monolithic app
└── simple_app.py           # Lightweight TOC-only version
```

### AI Services
- **OpenAI GPT-4o**: Text generation for TOC and book content
- **OpenAI DALL-E**: Front cover image generation  
- **Replicate Flux**: Back cover image generation
- **HAL9 Proxy**: Unified access to AI services

### Technology Stack
- **FastAPI**: REST API framework with automatic OpenAPI docs
- **WeasyPrint**: PDF generation from HTML/CSS
- **Pypandoc**: Markdown to HTML conversion
- **Pydantic**: Data validation and serialization
- **PIL**: Image processing and manipulation

### Generation Strategies
1. **Composite (Recommended)**: `generate-book-chapters` - TOC + selected chapters in one call
2. **Sequential**: Chapter-by-chapter with cross-chapter context
3. **Parallel**: Faster generation with independent chapters
4. **Legacy**: Original monolithic approach

### Data Flow
1. **TOC Generation**: Book idea → AI generates structured TOC
2. **Chapter Selection**: Choose specific chapters to generate
3. **Context-Aware Generation**: Each chapter has access to full TOC and book context
4. **Format Output**: Markdown → HTML → Styled PDF with pagination
5. **Cover Creation**: Book metadata → AI generates cover images → Assembled cover PDF

## Configuration

### Environment Variables
- `HAL9_TOKEN`: Required for AI service access

### Font Assets
The application includes multiple TTF fonts in the `fonts/` directory for cover text styling:
- Kanit (Bold/Regular)
- Roboto Condensed
- Noto Sans
- And more...

## Development

### Development Commands
```bash
# Run main app with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run simple version (TOC only)
uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000

# Run legacy version for comparison
uvicorn app_legacy:app --reload --host 0.0.0.0 --port 8001

# Test API endpoints
curl http://localhost:8000/test

# Access interactive demo
open http://localhost:8000/demo
```

### Testing
```bash
# Run unit tests
python run_tests.py

# Test mock endpoints (no dependencies required)
python test_mock_endpoints.py

# Or with pytest directly
pytest tests/ -v

# Test specific production endpoint
curl -X POST "http://localhost:8000/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Test Author", "book_idea": "Test concept", "chapters_to_generate": [1]}'

# Test specific mock endpoint (instant)
curl -X POST "http://localhost:8000/mock/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Test Author", "book_idea": "Test concept", "chapters_to_generate": [1]}'
```

## Troubleshooting

### WeasyPrint Installation Issues
If you encounter library loading errors with WeasyPrint:

1. Ensure all system dependencies are installed via Homebrew
2. Set the required environment variables:
   ```bash
   export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"
   export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
   ```
3. Use the simple version for TOC-only functionality if full version fails

### HAL9 Token Issues
- Verify your HAL9_TOKEN is correctly set
- Check token permissions for OpenAI and Replicate access
- Test with a simple TOC request first

## License

[Add your license information here]