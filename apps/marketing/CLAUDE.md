# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Local Development:**
```bash
quarto preview          # Start local dev server on port 4710
```

**Build:**
```bash
quarto render          # Generate static site to docs/ directory
```

**No testing setup** - The project uses a placeholder test script that exits with error.

## Architecture Overview

This is a **Quarto-based static website** with **Netlify serverless functions** for a book writing service called Proofbound. The site features dual pricing options with Stripe payments and HAL9 AI integration.

### Core Architecture
- **Frontend**: Quarto static site generator with custom CSS animations
- **Backend**: Netlify Functions (Node.js serverless)
- **Payment**: Stripe Checkout integration for automated service
- **AI Service**: HAL9 book generation API
- **Hosting**: Netlify with custom domain `proofbound.com`

### Dual Service Model
1. **Fully Automated ($49.95)**: Landing page → Stripe Checkout → Success page verification → HAL9 book generator
2. **Elite Edition (Custom Pricing)**: Landing page → Direct link to `app.proofbound.com` for human-crafted service

### User Flows
- **Automated Flow**: Payment verification prevents unauthorized access to premium AI tool
- **Elite Flow**: Direct redirect to external application for premium human service
- Serverless functions handle payment validation and HAL9 URL generation

## Key Files & Structure

**Content Files:**
- `index.qmd` - Landing page with dual pricing cards and animated theme
- `success.qmd` - Post-payment success page (only displays after payment verification)
- `about.qmd`, `cancel.qmd` - Supporting pages

**Styling:**
- `_resources/css/landing.css` - Main landing page styles including pricing card layouts
- `styles.css` - Global styles
- Custom pricing card design with premium Elite styling (gold accents, "PREMIUM" badge)

**Configuration:**
- `_quarto.yml` - Site config (theme: minty, fonts: Crimson Text, port: 4710, excludes CLAUDE.md from rendering)
- `netlify.toml` - Deployment config, redirect rules for payment verification
- `_resources/js/config.js` - Stripe configuration with live keys

**Serverless Functions:**
- `netlify/functions/verify-session.js` - Validates Stripe payment before allowing success page access
- `netlify/functions/hal9-embed.js` - Generates HAL9 iframe URL with API key

**Environment Variables Required:**
- `STRIPE_SECRET_KEY` - Stripe API secret key
- `HAL9_API_KEY` - HAL9 service API key

## Payment Integration Details

**Automated Service ($49.95):**
- Uses live price ID: `price_1RUa4cFVqC8fbxB6WWtakog4`
- External Stripe endpoint: `https://proofbound-stripe.netlify.app`
- Session verification enforced via Netlify redirect rules

**Elite Service:**
- Direct link to `app.proofbound.com` (opens in new tab)
- No payment processing on this site for Elite option

**Security Flow:**
- `/success.html` redirects to `/.netlify/functions/verify-session` (status 302)
- Function validates payment completion before serving success page
- HAL9 URL generation includes CORS protection for `proofbound.com`

## Pricing Card Implementation

The landing page features two distinct pricing options:
- **Fully Automated**: Standard blue styling with existing Stripe integration
- **Elite Edition**: Premium gold styling with "PREMIUM" badge, links to external app

CSS includes responsive design, hover effects, and glassmorphism styling for professional appearance.

## Deployment

- **Output Directory**: `docs/` (configured in `_quarto.yml`)
- **Functions Directory**: `netlify/functions/`
- **Domain**: Custom domain setup on Netlify
- **File Exclusions**: CLAUDE.md excluded from Quarto rendering
- No CI/CD configuration files present - likely using Netlify's Git-based deployment

## Development Notes

- Quarto preview runs on port 4710 (not default 3000)
- Site uses custom fonts (Crimson Text, Source Code Pro) with CSS loading order
- Pricing cards use CSS Grid with mobile responsiveness
- Elite option styled with premium visual indicators
- Uses dotenv for environment variable management in functions