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
- **`packages/ai-clients/`** - FastAPI server for AI service integrations (HAL9, OpenAI, Anthropic)
- **`packages/cc-template/`** - CLI tool for Quarto book generation with templates

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
- **FastAPI** for API services
- **Python 3.10** with modern tooling (uv, pytest)
- **AI Integration**: HAL9, OpenAI, Anthropic, Replicate
- **PDF Generation**: WeasyPrint
- **Book Templates**: Quarto publishing pipeline

## Project Structure

```
proofbound-monorepo/
├── apps/
│   ├── main-app/frontend/      # React application
│   └── marketing/              # Quarto marketing site
├── packages/
│   ├── ai-clients/            # FastAPI AI service
│   ├── cc-template/           # Book generation CLI
│   ├── book-engine/           # (planned)
│   └── shared-types/          # (planned)
├── tools/                     # Internal tooling (planned)
├── venv/                      # Python virtual environment
├── Taskfile.yml              # Task runner configuration
└── CLAUDE.md                  # Development guidance
```

## User Flow

1. **Marketing Site** (proofbound.com) - Landing page with dual pricing
2. **Automated Service** ($49.95) - Stripe checkout → AI book generation
3. **Elite Service** (Custom) - Direct link to React app for human-crafted books

## Environment Setup

### Prerequisites
- **Node.js** (for React frontend)
- **Python 3.10** (for AI services and book generation)
- **Quarto** (for marketing site and book templates)

### Environment Variables
Create `.env` files for:
- Supabase configuration (auth, database)
- AI service API keys (HAL9, OpenAI, Anthropic)
- Stripe configuration (payment processing)

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
- **Marketing site** deployed to proofbound.com with Stripe integration
- **React frontend** deployed to app.proofbound.com with Supabase auth and account management
- **AI clients** with multiple service integrations (HAL9, OpenAI, Anthropic)
- **Book generation CLI** with Quarto templates
- **Environment-aware navigation** between local and production deployments
- **Version management system** with semantic versioning and automated deployment tracking
- **Logo navigation convention** for intuitive user flow between marketing and app
- **Unified development workflow** with centralized environment variables

### 🔄 In Development  
- Frontend-API integration with new chapter-by-chapter endpoints
- Demo route implementation for lead generation
- Elite service dashboard for manual book processing
- Lulu print-on-demand integration

### 📋 Planned
- Bulk generation tools
- Analytics dashboard
- Quality control interfaces
- Google integration

## Recent Updates

### Recent Updates (July 2025)

#### Account Management & Navigation
- **Header component**: Added comprehensive account management with signin/signout, user menu, and navigation between dashboard and book generator
- **Logo navigation convention**: Implemented intuitive logo behavior (black logos → marketing site, blue logos → React app home)
- **Environment-aware routing**: All navigation intelligently switches between localhost and production URLs
- **Mobile responsive**: Account management works seamlessly across desktop and mobile devices

#### Version Management System
- **Semantic versioning**: Implemented proper version tracking with `src/version.ts` and automated bump scripts
- **Version display**: Inconspicuous version display at bottom of main page (e.g., "v1.0.0 (Dec 7, 2024)")
- **Deployment workflow**: Simple commands for version bumping before deployment (`task version:patch/minor/major`)
- **Automated tracking**: Version and build date automatically updated with each deployment

#### Infrastructure Improvements
- **Fixed deployment issues**: Resolved gitignore conflicts preventing deployment of frontend source files
- **Environment variable centralization**: All apps now use root `.env` file with proper Vite integration  
- **Task integration**: `task dev:all` successfully runs both sites with proper environment loading
- **Supabase auth fixes**: Improved signout handling and error management

## Contributing

This monorepo successfully unifies the Proofbound platform development while maintaining production deployments. The architecture supports rapid local development with seamless production deployment.

For detailed development guidance and architecture decisions, see [CLAUDE.md](./CLAUDE.md).