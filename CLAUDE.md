# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Proofbound Monorepo - Development Guide

## Current Status: Active Development
Monorepo migration complete. Core infrastructure operational with three active packages:
- ✅ **Main React App**: Production-ready with Supabase auth, Stripe payments, book generation
- ✅ **AI Clients API**: FastAPI server with HAL9/OpenAI integration, mock endpoints, demo interface  
- ✅ **CC Template CLI**: Python tool for Quarto book generation with templates
- 📅 **Marketing Site**: Quarto-based proofbound.com with Netlify deployment
- 🏗️ **Elite Dashboard**: Planned internal tooling (in apps/elite-dashboard/)

## Progress Update (July 2, 2025)
### ✅ Completed Infrastructure
- **AI Clients Package**: Full FastAPI implementation with chapter-by-chapter generation, mock API system for cost-free development, comprehensive demo interface
- **Frontend**: Production React app with authentication, payment processing, and book generation workflow
- **Testing**: Mock endpoints, unit tests, demo presets for rapid development
- **Deployment**: ✅ Marketing site live at proofbound.com, ✅ React app deployed to app.proofbound.com
- **Environment Setup**: Centralized .env configuration, Vite integration with monorepo structure
- **Development Workflow**: `task dev:all` runs both frontend and marketing simultaneously

### 🎯 Current Focus Areas
1. **Frontend-API Integration**: Connect React app to refactored AI endpoints (packages/ai-clients)
2. **Demo Route Implementation**: Add /demo to React app for lead generation
3. **Lulu Integration**: Print-on-demand service integration
4. **Elite Dashboard**: Internal tooling for manual book processing

### 🚀 Recent Achievements
- **Deployment Success**: Fixed gitignore issues and deployed React app to app.proofbound.com
- **Environment-Aware Navigation**: Marketing site Elite button and React app header logo correctly route between local and production environments
- **Account Management**: Added comprehensive header with signin/signout, user menu, and navigation
- **Version Management System**: Implemented semantic versioning with automated bump scripts and inconspicuous display
- **Logo Navigation Convention**: Black logos → marketing site, Blue logos → React app home (environment-aware)
- **Monorepo Task Integration**: Unified development commands with proper environment variable loading

## Architecture Overview
- `apps/main-app/frontend/` - Existing React app (Supabase auth, book generation)
- `packages/ai-clients/` - Will contain HAL9 + OpenAI clients
- `packages/cc-template/` - Will contain your Python book generation engine
- `tools/` - Elite service internal tooling

## Key Technical Stack
- Frontend: React + TypeScript + Supabase
- Backend: FastAPI (to be unified)
- AI: HAL9 API (cost-effective) + OpenAI (premium)
- Publishing: Quarto pipeline + Lulu print-on-demand
- Database: Supabase (will redesign schema)

## Development Roadmap

### Week 1-2: Frontend-API Integration
- Connect React app to new `/generate-book-chapters` endpoint
- Implement demo route in React app with AI Clients API
- Replace legacy API calls with modular endpoints
- Add outline editing capabilities to main app

### Week 3: Print Integration & Elite Tools  
- Lulu API integration for print-on-demand
- Elite dashboard initial implementation
- Quality control workflows

### Week 4: Launch Preparation
- Payment flow optimization
- Performance testing and monitoring
- Marketing site content updates
- Production deployment testing

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

### AI Clients Package (`packages/ai-clients/`)
- FastAPI server with multiple AI service integrations
- Services: HAL9, OpenAI, Anthropic, Replicate
- PDF generation with WeasyPrint
- Cover generation and book compilation

### CC Template Package (`packages/cc-template/`)
- CLI tool for Quarto book generation
- Entry point: `cc-template` command
- Templates in `/templates/` directory
- Uses uv for modern Python dependency management

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