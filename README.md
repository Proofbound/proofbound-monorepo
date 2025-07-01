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

**URLs:**
- Marketing Site: http://localhost:4710 (Quarto)
- Frontend App: http://localhost:5173 (React)

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
task dev:marketing    # Marketing site on localhost:4710  
task dev:all          # Both sites simultaneously
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
- Marketing site with Stripe integration
- React frontend with Supabase auth
- AI clients with multiple service integrations
- Book generation CLI with Quarto templates

### 🔄 In Development  
- Elite service dashboard
- Advanced book editing features
- Payment processing enhancements

### 📋 Planned
- Bulk generation tools
- Analytics dashboard
- Quality control interfaces
- Google integration

## Contributing

This is a fresh migration from separate repositories into a unified monorepo structure. The codebase maintains the original functionality while enabling shared development workflows.

For development guidance and architecture details, see [CLAUDE.md](./CLAUDE.md).