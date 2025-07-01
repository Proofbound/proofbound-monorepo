# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This is a Python FastAPI application for AI-powered book generation. Key commands:

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install fastapi uvicorn openai beautifulsoup4

# Install system dependencies (macOS - required for full app.py)
brew install python-tk pango gdk-pixbuf libffi gobject-introspection cairo gtk+3

# Set required environment variable
export HAL9_TOKEN=your_hal9_token_here

# For local development, API_BASE_URL is optional (defaults to relative URLs)
# For deployment, set the appropriate base URL:
# export API_BASE_URL=https://api.hal9.com/books/bookgeneratorapi/proxy

# Run the simple version (TOC generation only - no system deps needed)
uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000

# Run the refactored version (all features - requires system dependencies)
# Note: If WeasyPrint fails to load, set these environment variables:
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run the legacy version (if needed for comparison)
uvicorn app_legacy:app --reload --host 0.0.0.0 --port 8001

# Test the API
curl http://localhost:8000/test

# Generate TOC + first chapter
curl -X POST "http://localhost:8000/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Book Title", "author": "Author", "book_idea": "Book concept", "chapters_to_generate": [1]}'

# Generate TOC + multiple chapters  
curl -X POST "http://localhost:8000/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Book Title", "author": "Author", "book_idea": "Book concept", "chapters_to_generate": [1,2,3]}'

# MOCK MODE - Test without AI costs
curl -X POST "http://localhost:8000/mock/toc" \
  -H "Content-Type: application/json" \
  -d '{"title": "Book Title", "author": "Author", "book_idea": "Book concept"}'

# Mock chapter generation (instant response)
curl -X POST "http://localhost:8000/mock/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Book Title", "author": "Author", "book_idea": "Book concept", "chapters_to_generate": [1,2]}'

# Run unit tests
python run_tests.py

# Or run tests directly with pytest (after installing dependencies)
pytest tests/ -v
```

## Architecture Overview

This project contains three FastAPI applications for AI-powered book generation:

1. **`simple_app.py`** - Lightweight version with TOC generation only (no system dependencies)
2. **`app.py`** - Refactored modular version with chapter-by-chapter generation (requires WeasyPrint system dependencies)
3. **`app_legacy.py`** - Original monolithic version (for comparison/fallback)

Both applications integrate with AI services via HAL9 proxy:

- **OpenAI GPT-4o** (via HAL9 proxy) for text generation and front cover images
- **Replicate Flux** (via HAL9 proxy) for back cover image generation
- **WeasyPrint** for PDF generation from HTML/CSS (full version only)
- **Pypandoc** for Markdown to HTML conversion (full version only)

### Current API Endpoints

**Simple version (`simple_app.py`):**
- `GET /test` - Health check endpoint
- `POST /toc` - Generate table of contents from book idea
- `GET /demo` - Interactive demo interface for TOC testing
- `GET /demo/presets` - Available demo book examples

**Refactored version (`app.py`):**
- `GET /test` - Health check endpoint  
- `POST /toc` - Generate table of contents from book idea
- `POST /draft` - Generate full book content in Markdown (legacy compatibility)
- `POST /generate-chapter` - Generate single chapter with context
- `POST /generate-book` - Generate complete book chapter-by-chapter
- `POST /generate-book-chapters` - **IMPLEMENTED**: Generate TOC + selected chapters (stateless)
- `POST /draft-legacy` - Legacy monolithic draft generation for backwards compatibility
- `POST /pdf` - Convert Markdown to formatted PDF
- `POST /cover` - Generate book cover PDF (front/back/spine)
- `GET /demo` - Interactive demo interface with mock mode toggle
- `GET /demo/presets` - Available demo book examples

**🚀 NEW: Mock Endpoints (No AI costs):**
- `GET /mock/test` - Mock health check endpoint
- `POST /mock/toc` - Mock table of contents generation (instant)
- `POST /mock/draft` - Mock full book draft generation
- `POST /mock/generate-chapter` - Mock single chapter generation
- `POST /mock/generate-book` - Mock complete book generation
- `POST /mock/generate-book-chapters` - Mock TOC + selected chapters
- `POST /mock/pdf` - Mock PDF generation (returns sample PDF)
- `POST /mock/cover` - Mock cover generation (returns sample PDF)

**Legacy version (`app_legacy.py`):**
- `GET /test` - Health check endpoint
- `POST /toc` - Generate table of contents from book idea
- `POST /draft` - Original monolithic draft generation
- `POST /pdf` - Convert Markdown to formatted PDF
- `POST /cover` - Generate book cover PDF (front/back/spine)
- `GET /demo` - Interactive demo interface
- `GET /demo/presets` - Available demo book examples

### PLANNED ARCHITECTURE CHANGES

The following improvements are planned to support testing, demos, and eventual frontend integration:


#### Phase 1: Demo Interface (Immediate)
Add `/demo` route with crude HTML interface for testing and partner demonstrations:

```
Current API Endpoints + New Demo Routes:
├── /toc              - Generate table of contents  
├── /draft            - Generate full book draft (will be refactored)
├── /pdf              - Generate formatted PDF
├── /cover            - Generate book cover
└── /demo             - NEW: Demo interface with presets
    ├── /demo/        - HTML demo page
    ├── /demo/presets - Available demo book examples
    └── /demo/test-*  - Individual endpoint testing
```

**Demo Requirements:**
- Simple HTML interface with preset book examples
- Real AI calls (not mocked) for robustness testing  
- Technical details visible (timing, costs, JSON responses)
- Easy modification as APIs evolve

#### Phase 2: Chapter-by-Chapter Generation
Break monolithic `/draft` into granular chapter generation with composite endpoint approach:

```
Planned API Refactoring:
├── /generate-book-chapters - NEW: Generate TOC + selected chapters in one call
├── /generate-chapter       - FUTURE: Individual chapter generation (when frontend is smarter)
├── /extract-context        - FUTURE: Extract narrative elements for coherence
└── /demo/chapter-test      - Test different chapter generation strategies
```

**Implementation Strategy:**
Use composite endpoint pattern to handle "dumb frontend" problem while maintaining stateless design.

**New Endpoint Specification:**
```python
@app.post("/generate-book-chapters")
def generate_book_chapters(req: BookChaptersRequest):
    class BookChaptersRequest(BaseModel):
        title: str
        author: str  
        book_idea: str
        chapters_to_generate: List[int] = [1]  # Default: just first chapter
    
    # Generate TOC first (internal)
    toc = toc_generator.generate(req.title, req.author, req.book_idea)
    
    # Generate requested chapters with full context
    chapters = []
    for chapter_num in req.chapters_to_generate:
        if chapter_num <= len(toc):
            chapter = chapter_generator.generate(
                chapter_outline=toc[chapter_num - 1],
                book_metadata=req,
                chapter_number=chapter_num,
                full_toc=toc  # Available for context
            )
            chapters.append(chapter)
    
    return {
        "toc": toc,
        "chapters": chapters,
        "generated_chapters": req.chapters_to_generate
    }
```

**Benefits:**
- **Stateless**: No cache or session management needed
- **Frontend-friendly**: Single API call generates TOC + chapters
- **Flexible**: Can generate 1 or multiple chapters per call
- **Future-proof**: When frontend gets smarter, can split into separate `/toc` and `/generate-chapter` calls
- **Cost-efficient**: Generate only requested chapters
- **Context-aware**: Each chapter has access to full TOC for coherence

#### Phase 3: Context Management (Future)
Add narrative coherence while maintaining stateless design:

```python
# Context passed explicitly, no backend state
@app.post("/generate-chapter")
def generate_chapter(req: ChapterRequest):
    return chapter_generator.generate(
        chapter_outline=req.chapter_outline,
        book_context=req.context,  # Frontend responsibility
        previous_chapters=req.context.previous_chapters
    )
```

### Target Architecture for Frontend Integration

This stateless API will eventually serve:
- `proofbound.com` - Landing page  
- `app.proofbound.com` - User-facing app (Netlify + Supabase)

Demo interface simulates how real frontend will orchestrate API calls.

## Demo Interface Specifications

### Target Users
- Internal developers testing new features
- Technical partners evaluating capabilities
- Feature demonstrations (crude but functional UI acceptable)

### Preset Examples
```python
DEMO_PRESETS = {
    "eyes_health": {
        "title": "Eyes on Health", 
        "author": "Richard Sprague",
        "book_idea": "AI-powered retinal imaging for wellness assessment..."
    },
    "microbiome": {
        "title": "The Microbiome Revolution",
        "author": "Dr. Sarah Chen", 
        "book_idea": "Personal microbiome optimization strategies..."
    },
    "novel_test": {
        "title": "The Silicon Valley Heist",
        "author": "Alex Morgan",
        "book_idea": "Tech thriller about AI startup corporate espionage..."
    }
}
```

### Demo Features
- Dropdown preset selector (avoid re-entering data)
- Editable fields for customization
- Real-time timing and cost tracking
- Raw JSON response display
- Individual endpoint testing
- Complete workflow demonstrations

## Testing Strategy

The project includes comprehensive unit tests plus planned demo/integration testing:

### Current Testing
- **`tests/test_models.py`** - Tests for Pydantic models and validation
- **`tests/test_simple_app.py`** - Tests for simple_app.py endpoints and functions
- **`tests/test_app.py`** - Tests for full app.py endpoints and functions
- **`tests/conftest.py`** - Shared test fixtures and mocks

### Planned Testing Additions

#### Demo Tests (Fast)
- Validate demo interface functionality
- Test preset data integrity
- Ensure demo represents real API behavior

#### Integration Tests (Slower)
- Real AI calls with small inputs
- End-to-end workflow testing  
- Performance benchmarking with timing/cost tracking

#### Chapter Generation Tests
- Test individual chapter generation
- Validate chapter sequencing
- Compare coherence strategies

### Running Tests

```bash
# Current test setup
python run_tests.py

# Test mock endpoints (no AI dependencies)
python test_mock_endpoints.py

# Planned additions
pytest tests/test_demo.py -v          # Demo functionality
pytest tests/test_integration.py -v   # Full workflows  
pytest tests/test_performance.py -v   # Timing/cost tests
```

## Implementation Roadmap

### ✅ COMPLETED: Mock API System
- [x] **Mock Endpoints**: Complete `/mock/*` endpoint suite
  - [x] All 8 mock endpoints implemented with realistic responses
  - [x] Mock data system with proper Pydantic model support
  - [x] Sample PDF file for cover/PDF mock downloads
- [x] **Demo Interface Enhancements**: 
  - [x] Mock mode toggle in demo interface
  - [x] Dynamic endpoint routing (mock vs real)
  - [x] Visual feedback for mock mode status
  - [x] Fixed CORS issues for local development
- [x] **Testing Infrastructure**:
  - [x] `test_mock_endpoints.py` test suite
  - [x] Comprehensive mock response validation
  - [x] FastAPI integration testing for mock endpoints

### ✅ COMPLETED: Core Features
- [x] **Chapter Generation System**: 
  - [x] `/generate-book-chapters` composite endpoint
  - [x] `BookChaptersRequest` Pydantic model
  - [x] Chapter-by-chapter generation with context
  - [x] Stateless design for frontend integration
- [x] **Demo Interface**:
  - [x] `/demo` route with HTML interface
  - [x] Demo presets file with realistic examples
  - [x] Performance tracking and timing display
  - [x] Mock/real mode switching capability

### Short-term (Performance & Analytics)
- [ ] Performance comparison testing
  - [ ] Compare `/draft` (full book) vs `/generate-book-chapters` (selective)
  - [ ] Measure cost per chapter in real vs mock mode
  - [ ] Test chapter quality and coherence
- [ ] Enhanced analytics
  - [ ] Cost tracking per endpoint
  - [ ] Response time monitoring
  - [ ] Usage metrics collection

### Medium-term (Context Management)
- [ ] Add `/extract-context` endpoint
- [ ] Implement context-passing patterns
- [ ] Advanced demo workflows
- [ ] Coherence quality metrics

### Current File Structure

```
bookgeneratorapi/
├── app.py                     # ✅ Main FastAPI app with mock endpoints
├── simple_app.py              # Lightweight version (TOC only)
├── app_legacy.py              # Original monolithic version
├── demo/                      # ✅ Demo interface (IMPLEMENTED)
│   ├── __init__.py
│   ├── routes.py              # ✅ Demo routes with mock mode toggle
│   └── presets.py             # ✅ Demo presets
├── mock_data/                 # ✅ NEW: Mock response system
│   ├── responses.py           # ✅ Mock data generation
│   └── Eyes_on_Health_cover.pdf  # ✅ Sample PDF for mock downloads
├── models/                    # Pydantic models
│   ├── __init__.py
│   ├── request_models.py      # Request models
│   ├── chapter_models.py      # Chapter generation models
│   └── section_model.py       # TOC section model
├── services/                  # Modular services
│   ├── __init__.py
│   ├── ai_client.py           # HAL9 proxy integration
│   ├── chapter_generator.py   # Chapter-by-chapter generation
│   ├── cover_generator.py     # AI cover generation
│   └── pdf_generator.py       # PDF formatting
├── tests/                     # Test suites
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures
│   ├── test_app.py            # App endpoint tests
│   ├── test_models.py         # Model validation tests
│   └── test_simple_app.py     # Simple app tests
├── test_mock_endpoints.py     # ✅ NEW: Mock endpoint validation
├── fonts/                     # Font files for PDF generation
├── requirements.txt           # Python dependencies
└── run_tests.py              # Test runner
```


## Data Flow

### Current
1. **TOC Generation**: Book idea → structured JSON table of contents
2. **Draft Generation**: TOC + metadata → complete Markdown manuscript (monolithic)
3. **PDF Generation**: Markdown → HTML → styled PDF with proper pagination
4. **Cover Generation**: Book metadata → AI-generated images → assembled cover PDF

### Current + Planned (Chapter-by-Chapter)
1. **TOC Generation**: Book idea → structured JSON table of contents
2. **Selective Chapter Generation**: Book idea + chapter selection → TOC + requested chapters
3. **Legacy Full Book**: TOC + metadata → complete Markdown manuscript (existing `/draft`)
4. **PDF/Cover Generation**: Same as current

**Example Usage:**
```bash
# Generate TOC + first chapter only
curl -X POST "/generate-book-chapters" \
  -d '{"title": "Eyes on Health", "author": "Richard", "book_idea": "...", "chapters_to_generate": [1]}'

# Generate TOC + chapters 1, 2, 3
curl -X POST "/generate-book-chapters" \
  -d '{"title": "Eyes on Health", "author": "Richard", "book_idea": "...", "chapters_to_generate": [1,2,3]}'

# Full book (existing endpoint)
curl -X POST "/draft" -d '{"title": "Eyes on Health", "author": "Richard", "book_idea": "...", "toc": [...]}'
```

### Future (Context-Aware)
1. **TOC Generation**: Book idea → structured JSON + narrative outline
2. **Context Extraction**: Previous chapters → character/plot/terminology context
3. **Coherent Chapter Generation**: Chapter outline + accumulated context → coherent chapter
4. **Assembly & Export**: Coherent chapters → formatted outputs

## Success Metrics

### Demo Effectiveness
- Can demonstrate new features in < 5 minutes
- Preset examples work reliably with real AI
- Technical details visible for partner discussions
- Easy to modify as APIs evolve

### API Robustness  
- Consistent response times per operation
- Predictable costs with granular tracking
- Graceful error handling and recovery
- Scalable to book-length content

### Development Velocity
- Easy to test new features in isolation
- Quick feedback on API changes
- Clear performance impact visibility
- Modular testing approach

## Environment Requirements

**All versions:**
- `HAL9_TOKEN` environment variable must be set for AI service access
- `API_BASE_URL` environment variable for demo interface deployment (optional, defaults to relative URLs for local development)

**Full version only:**
- System dependencies for WeasyPrint (see installation commands above)
- Pandoc (auto-downloaded if missing)
- Environment variables for WeasyPrint library loading (PKG_CONFIG_PATH and DYLD_LIBRARY_PATH)

**Demo interface:**
- No additional dependencies (uses existing FastAPI setup)
- Same HAL9_TOKEN for real AI calls
- Configure API_BASE_URL for different deployment environments:
  - **Local development**: Leave unset (uses relative URLs like `/toc`)
  - **HAL9 deployment**: `API_BASE_URL=https://api.hal9.com/books/bookgeneratorapi/proxy`
  - **Other deployments**: Set to appropriate base URL for your environment

## Key Components

- **AI Client Configuration**: Uses HAL9 proxy tokens for OpenAI and Replicate access
- **PDF Styling**: Custom CSS for book formatting (6×9 inch pages, headers, TOC)
- **Cover Assembly**: Combines front/back images with spine and text overlays
- **Font Assets**: Multiple TTF fonts included for cover text styling
- **Demo Interface**: Technical testing UI with preset examples and performance tracking

## 🚀 Mock API System

### Overview
The mock API system provides cost-free testing and development capabilities by returning realistic responses without calling expensive AI services. Perfect for:

- **Frontend development**: Test UI without AI costs
- **Integration testing**: Validate app logic with predictable responses  
- **Demonstrations**: Show API capabilities without live AI dependencies
- **External app development**: Other applications can integrate safely

### Usage

**Demo Interface Mock Mode:**
1. Visit http://localhost:8000/demo
2. Check "🚀 Mock Mode" checkbox
3. All API calls automatically use `/mock/*` endpoints
4. Instant responses with realistic data structure

**Direct API Calls:**
```bash
# Mock TOC generation (instant)
curl -X POST "http://localhost:8000/mock/toc" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Test Author", "book_idea": "AI book concept"}'

# Mock chapter generation
curl -X POST "http://localhost:8000/mock/generate-book-chapters" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Test Author", "book_idea": "AI book", "chapters_to_generate": [1,2]}'
```

**External Applications:**
- Use `http://localhost:8000/mock/*` endpoints for development
- Switch to `http://localhost:8000/*` for production
- Same request/response schemas as real endpoints

### Mock Response Features
- **Realistic data structure**: Matches production Pydantic models exactly
- **Cost estimates**: Includes mock timing and cost data for testing
- **PDF downloads**: Returns actual sample PDF files for cover/PDF endpoints
- **Context awareness**: Chapter generation uses actual TOC data for coherence
- **Instant responses**: Sub-second response times for fast iteration

## Important Notes

- **Mock mode**: Use `/mock/*` endpoints for cost-free development and testing
- **Real mode**: Use regular endpoints when you need actual AI generation
- Start with `simple_app.py` for easy setup and TOC generation testing
- Use `app.py` for full features including mock endpoints
- WeasyPrint system dependencies can be complex on some systems
- Font files are stored in `fonts/` directory for cover generation
- HAL9 proxy provides unified access to OpenAI and Replicate APIs
- Demo interface supports both mock and real AI calls via toggle
- Stateless design enables future frontend integration (app.proofbound.com)

## Getting Started

### For Development (Mock Mode)
1. **Start server**: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`
2. **Visit demo**: http://localhost:8000/demo
3. **Enable mock mode**: Check the "🚀 Mock Mode" checkbox
4. **Test endpoints**: Use presets to test all functionality instantly
5. **No setup required**: Works without HAL9_TOKEN or system dependencies

### For Production (Real AI)
1. **Set environment**: `export HAL9_TOKEN=your_token_here`
2. **Install dependencies**: For PDF generation (optional)
3. **Visit demo**: http://localhost:8000/demo  
4. **Use real mode**: Leave mock mode unchecked
5. **Test with small inputs**: Use presets for cost-effective testing