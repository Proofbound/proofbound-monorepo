# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Proofbound Monorepo - Development Guide

## Current Status: Fresh Migration
Just migrated from separate webapp + API to unified monorepo. Ready for dual-track development.

## Immediate Goals (Next 3-4 weeks)
1. **Self-Service Enhancements**: Add outline editing + Lulu integration to existing React app
2. **Elite Service Dashboard**: Internal tooling for manual book generation  
3. **Backend Unification**: Refactor HAL9 API calls into shared ai-clients package

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

## Development Priority
Week 1: Lulu integration for self-service
Week 2: Outline editing improvements  
Week 3: Elite service dashboard
Week 4: Payment processing + launch prep

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