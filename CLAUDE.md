# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Proofbound Monorepo - Development Guide

## Current Status: HAL9 API Integration Complete (July 4, 2025)

### ✅ Completed Infrastructure
- **Main React App**: Production-ready with Supabase auth, Stripe payments
- **Demo Route**: **NOW LIVE** with real HAL9 AI book generation
- **HAL9 API Integration**: Complete book generation pipeline through Supabase Edge Functions
- **Quarto Project Export**: Full downloadable Quarto projects with generated content
- **Marketing Site**: Live at proofbound.com with simplified landing page
- **Development Workflow**: Streamlined for rapid iteration

### 🎯 Current Architecture: HAL9 Direct Integration
**Successfully Implemented HAL9 API Integration**

**✅ Production Architecture:**
- **HAL9 API Integration**: Cost-effective AI book generation via existing edge functions
- **Supabase Edge Functions**: `generate-toc`, `generate-content` for HAL9 API calls
- **React Frontend**: Real-time AI integration with graceful fallbacks
- **Quarto Project Generation**: Complete downloadable book projects
- **TypeScript Integration**: Full type safety and HAL9 API compatibility

### 🚀 Recent Achievements (July 4, 2025)
- **HAL9 API Integration**: Complete book generation using existing edge functions
- **Real AI Demo**: Replaced mock data with actual HAL9 AI-generated content
- **Quarto Export**: Full project generation with chapters, config, and templates
- **Content Cleaning**: Automatic removal of duplicate H1 titles for proper Quarto format
- **Graceful Fallbacks**: Demo works reliably with both API success and failure scenarios
- **Type Safety**: Comprehensive TypeScript types for all HAL9 API interactions

### 🎯 Next Phase: Production Deployment
1. **Test Integration**: Verify complete workflow with HAL9 API
2. **Performance Optimization**: Monitor API costs and response times
3. **User Experience**: Refine demo flow and error handling
4. **Production Deploy**: Merge to main and deploy to production
5. **Analytics**: Track demo usage and conversion rates

## Architecture Overview
- `apps/main-app/frontend/` - React app with Supabase auth, payment processing
- `packages/cc-template/` - Python CLI tool for Quarto book generation with AI
- `apps/marketing/` - Quarto-based marketing site (proofbound.com)
- `tools/` - Elite service internal tooling (planned)

## Key Technical Stack
- **Frontend**: React + TypeScript + Supabase + Tailwind CSS
- **Book Generation**: HAL9 API via Supabase Edge Functions
- **AI Services**: HAL9 API (cost-effective book generation)
- **Project Export**: Quarto → PDF/HTML/EPUB with JSZip download
- **Database**: Supabase (auth, payments, user data, book projects)
- **Publishing**: Quarto → PDF/HTML/EPUB + Lulu print-on-demand (future)

## HAL9 API Integration (✅ Complete)

### Phase 1: HAL9 Integration (✅ Complete)
- **Book Service**: Central orchestration service for HAL9 API calls
- **Edge Functions**: Utilize existing `generate-toc` and `generate-content` functions
- **Type Safety**: Comprehensive TypeScript types for HAL9 API responses
- **Content Processing**: Automatic cleaning of duplicate H1 titles for Quarto compatibility
- **Error Handling**: Graceful fallbacks for reliable demo experience

### Phase 2: Quarto Export (✅ Complete)
- **Project Generation**: Complete Quarto book projects with chapters, config, templates
- **ZIP Download**: Client-side project packaging with JSZip
- **Template System**: Comprehensive Quarto templates with proper frontmatter
- **File Structure**: Proper chapter organization with slugified filenames
- **Metadata Integration**: Book title, author, and outline data in Quarto config

### Phase 3: Future Enhancements
- **Database Integration**: Save/load book projects for authenticated users
- **Publishing Pipeline**: Lulu API integration for print-on-demand
- **Enhanced UI**: Project management interface with outline editing
- **Analytics**: Usage tracking and conversion optimization

## Development Commands

### Frontend Development (React App)
```bash
# Navigate to main app
cd apps/main-app/frontend/

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Python Development
```bash
# Activate virtual environment
source venv/bin/activate

# AI Clients FastAPI Server
cd packages/ai-clients/
pip install -r requirements.txt
python app.py  # or uvicorn app:app --reload

# CC Template CLI Tool
cd packages/cc-template/
uv sync  # Install dependencies with uv
uv run cc-template --help  # Run CLI tool
pytest  # Run tests
```

## Architecture Details

### Monorepo Structure
- **No workspace management**: Each package manages dependencies independently
- **Mixed package managers**: npm for frontend, pip + uv for Python packages
- **Active components**: main-app/frontend, ai-clients, cc-template
- **Planned components**: elite-dashboard, marketing site, tools/*

### Main Application (`apps/main-app/frontend/`)
- React 18 + TypeScript + Vite
- Supabase for auth and database
- Tailwind CSS for styling
- Production-ready with full user authentication

### CC Template Package (`packages/cc-template/`)
- **Complete CLI tool** for Quarto book generation with AI integration
- **Entry point**: `cc-template` command with subcommands (new, outline, generate, build, config)
- **AI Integration**: OpenAI GPT-4 and Anthropic Claude APIs for content generation
- **Template System**: Jinja2-based templates with YAML configuration
- **Output Formats**: HTML, PDF, EPUB via Quarto rendering
- **Project Structure**: Creates structured book projects with chapters, config, and build system
- **Development**: Uses uv for modern Python dependency management

## Testing
```bash
# Python tests (cc-template)
cd packages/cc-template/
pytest
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m slow      # Slow tests only

# No frontend tests configured yet
```

## Environment Setup
- Python 3.10 required
- Environment variables needed for AI services (see .env files)
- Supabase configuration for frontend auth

## Development Commands

# Start development servers
task dev:frontend     # React app on localhost:3000
task dev:marketing    # Marketing site on localhost:3001  
task dev:all         # Both simultaneously

# Setup
task install         # Install all dependencies
task setup:python    # Set up Python virtual environment

# Build
task build:frontend  # Production React build
task build:marketing # Production marketing build

# Version Management
task version:patch    # Bump patch version (1.0.0 -> 1.0.1)
task version:minor    # Bump minor version (1.0.0 -> 1.1.0) 
task version:major    # Bump major version (1.0.0 -> 2.0.0)