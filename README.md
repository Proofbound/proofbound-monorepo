# Proofbound Monorepo

Transform your ideas into professionally formatted books with Proofbound's AI-powered platform and expert services.

## Quick Start

```bash
# Install task runner (if not already installed)
brew install go-task/tap/go-task

# Install all dependencies
task install

# Start both sites for development
task dev:all
```

**Development URLs:**
- Marketing Site: http://localhost:8888 (Netlify dev with functions)
- Frontend App: http://localhost:5173 (React with Vite)

**Production URLs:**
- Marketing Site: https://proofbound.com
- Frontend App: https://app.proofbound.com

## Architecture

This monorepo contains two main applications and supporting packages:

### Applications
- **`apps/marketing/`** - Marketing website (proofbound.com) built with Quarto
- **`apps/main-app/frontend/`** - React web application (app.proofbound.com) with Supabase auth

### Packages
- **`packages/cc-template/`** - Complete CLI tool for AI-powered Quarto book generation
- **`packages/ai-clients/`** - ⚠️ FastAPI server (being phased out for cc-template integration)

## Development Commands

### Core Development
```bash
task dev:frontend     # React app on localhost:5173
task dev:marketing    # Marketing site on localhost:8888 (Netlify dev)
task dev:all          # Both sites simultaneously
```

### Version Management
```bash
task version:patch    # Bump patch version (1.0.0 -> 1.0.1)
task version:minor    # Bump minor version (1.0.0 -> 1.1.0) 
task version:major    # Bump major version (1.0.0 -> 2.0.0)
```

### Setup & Installation
```bash
task install         # Install all dependencies
task setup:python    # Set up Python virtual environment
```

### Building
```bash
task build:frontend  # Production React build
task build:marketing # Production Quarto build
task build:all       # Build everything
```

### Testing & Quality
```bash
task lint:frontend   # Lint React code
task test:python     # Run Python tests
task clean           # Clean build artifacts
```

## Technology Stack

### Frontend Stack
- **React 18** + TypeScript + Vite
- **Supabase** for authentication and database
- **Tailwind CSS** for styling
- **Stripe** for payment processing

### Marketing Stack
- **Quarto** static site generator
- **Netlify Functions** for serverless backend
- Custom animations and responsive design

### Backend Stack
- **HAL9 API** for cost-effective AI book generation
- **Supabase Edge Functions** for serverless AI API calls
- **Python 3.10** with modern tooling (uv, pytest)
- **Publishing Pipeline**: Quarto → PDF/HTML/EPUB
- **JSZip** for client-side project packaging and downloads

## Project Structure

```
proofbound-monorepo/
├── apps/
│   ├── main-app/frontend/      # React application
│   └── marketing/              # Quarto marketing site
├── packages/
│   ├── cc-template/           # Complete AI-powered book generation CLI
│   ├── ai-clients/            # (being phased out)
│   ├── book-engine/           # (planned)
│   └── shared-types/          # (planned)
├── tools/                     # Internal tooling (planned)
├── venv/                      # Python virtual environment
├── Taskfile.yml              # Task runner configuration
└── CLAUDE.md                  # Development guidance
```

## User Flow

1. **Marketing Site** (proofbound.com) - Simplified landing page with demo button
2. **Demo Route** (/demo) - Live AI book generation with HAL9 API integration
3. **Full Service** - React app with Supabase auth → HAL9 API book generation
4. **Elite Service** - Manual book processing with internal tools

## Environment Setup

### Prerequisites
- **Node.js** (for React frontend)
- **Python 3.10** (for AI services and book generation)
- **Quarto** (for marketing site and book templates)

### Environment Variables
Create `.env` files for:
- Supabase configuration (auth, database)
- HAL9 API token for AI book generation
- Stripe configuration (payment processing)

**Note**: Demo route uses HAL9 API with graceful fallbacks when unavailable.

**Marketing Site Stripe Setup:**
The marketing site requires a separate Stripe configuration file:
```bash
cd apps/marketing/_resources/js/
cp config.js.example config.js
# Edit config.js with your actual Stripe publishable key and price ID
```
Note: `config.js` is in .gitignore and should not be committed.

### First-Time Setup
```bash
# Clone and navigate to repo
git clone <repo-url>
cd proofbound-monorepo

# Set up Python environment
task setup:python
source venv/bin/activate

# Install all dependencies
task install

# Start development
task dev:all
```

## Development Status

### ✅ Production Ready
- **Marketing site** deployed to proofbound.com with simplified landing page
- **React frontend** deployed to app.proofbound.com with Supabase auth and account management  
- **HAL9 API Integration** complete with real AI book generation via Supabase Edge Functions
- **Demo route** with live AI-powered book generation (HAL9 API + graceful fallbacks)
- **Quarto Project Export** complete downloadable projects with generated content
- **Environment-aware navigation** between local and production deployments
- **Version management system** with semantic versioning and automated deployment tracking
- **Logo navigation convention** for intuitive user flow between marketing and app

### 🔄 In Development  
- **Performance optimization**: Monitor HAL9 API costs and response times
- **User experience refinement**: Enhanced demo flow and error handling
- **Database integration**: Save/load book projects for authenticated users
- **Elite service dashboard** for manual book processing
- **Lulu print-on-demand integration**

### 📋 Planned
- Bulk generation tools
- Analytics dashboard
- Quality control interfaces
- Google integration

## Recent Updates

### HAL9 API Integration Complete (July 4, 2025)

#### Live AI Book Generation
- **HAL9 API Integration**: Complete book generation pipeline using existing Supabase Edge Functions
- **Real AI Demo**: Replaced mock data with actual AI-generated content from HAL9 API
- **Graceful Fallbacks**: Demo works reliably with both API success and failure scenarios
- **Type Safety**: Comprehensive TypeScript types for all HAL9 API interactions

#### Quarto Project Export
- **Complete Project Generation**: Full Quarto book projects with chapters, config, and templates
- **ZIP Download**: Client-side project packaging using JSZip
- **Content Cleaning**: Automatic removal of duplicate H1 titles for proper Quarto format
- **File Structure**: Proper chapter organization with slugified filenames and metadata

#### Production-Ready Integration
- **Existing Edge Functions**: Leveraged deployed `generate-toc` and `generate-content` functions
- **Cost-Effective**: HAL9 API provides affordable AI generation compared to direct OpenAI/Anthropic
- **No Backend Required**: Pure frontend integration with Supabase Edge Functions
- **Immediate Deployment**: Ready for production without additional infrastructure

## Contributing

This monorepo successfully unifies the Proofbound platform development while maintaining production deployments. The architecture supports rapid local development with seamless production deployment.

For detailed development guidance and architecture decisions, see [CLAUDE.md](./CLAUDE.md).