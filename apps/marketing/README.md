# Proofbound Website

A Quarto-based landing page for Proofbound, an AI-powered book writing service with Stripe payment integration and serverless backend functions.

## Features

- **Dual Pricing Options**: Fully automated AI book generation ($49.95) and Elite human-crafted service
- **Stripe Integration**: Secure payment processing with session verification
- **HAL9 AI Integration**: Book generation API for automated service
- **Animated Landing Page**: Custom CSS animations and interactive elements
- **Serverless Backend**: Netlify Functions for payment verification and API integration

## Architecture

- **Frontend**: Quarto static site generator with custom CSS
- **Backend**: Netlify Functions (Node.js serverless)
- **Payment**: Stripe Checkout with live keys
- **AI Service**: HAL9 book generation API
- **Hosting**: Netlify with custom domain `proofbound.com`

## Development

### Prerequisites
- Quarto CLI installed
- Node.js for serverless functions

### Local Development
To run the full site with serverless functions locally, you'll need the Netlify CLI.

```bash
npm install -g netlify-cli # Install Netlify CLI (one-time install)
netlify dev                # Starts Quarto preview and serverless functions
```

### Build
```bash
quarto render          # Generate static site to docs/ directory
```

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd proofbound-web
   ```

2. **Configure Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env and add your actual API keys
   ```

3. **Configure Stripe Keys**
   ```bash
   cp _resources/js/config.js.example _resources/js/config.js
   # Edit config.js and add your actual Stripe keys
   ```

### Environment Variables
Required for serverless functions:
- `STRIPE_SECRET_KEY` - Stripe API secret key
- `HAL9_API_KEY` - HAL9 service API key

Required for frontend (in config.js):
- Stripe publishable key
- Stripe price ID

## Project Structure

- `index.qmd` - Landing page with pricing options
- `success.qmd` - Post-payment success page
- `netlify/functions/` - Serverless functions for payment and API integration
- `_resources/` - Static assets, CSS, and JavaScript
- `docs/` - Generated static site output

## Deployment

This project is designed for seamless deployment on Netlify via a Git-based workflow.

1.  **Connect Repository**: Link your Git repository (e.g., GitHub) to a new site on Netlify.
2.  **Build Settings**: Configure the following settings in the Netlify UI:
    -   **Build command**: `quarto render`
    -   **Publish directory**: `docs/`
    -   **Functions directory**: `netlify/functions/` (usually detected automatically)
3.  **Environment Variables**: This is a critical step. Your serverless functions need API keys to work in production.
    -   In your Netlify site dashboard, go to **Site configuration** > **Build & deploy** > **Environment**.
    -   Add the same environment variables listed in your `.env.example` file (e.g., `STRIPE_SECRET_KEY`, `HAL9_API_KEY`). These are kept secure on Netlify and are injected during the build and at runtime.
4.  **Deploy**: Push your code to the main branch of your repository. Netlify will automatically trigger a build, render your Quarto site, and deploy your serverless functions.

Your functions will be available at `https://your-site-name.netlify.app/.netlify/functions/<function-name>`.

### Notes
- The `.env` file is only for local development with `netlify dev` and should be listed in your `.gitignore` file. It will not be used by Netlify for production builds.
- Any push to your connected main branch will trigger a new deployment of both the site and the functions.
