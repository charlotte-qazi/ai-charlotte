# Deployment Guide

## Environment Variables for Railway (Backend)

### Required Environment Variables

Set these in Railway's environment variables section:

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database (Qdrant)
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=personal_docs

# Database (Supabase)
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# GitHub Integration (Optional)
GITHUB_USERNAME=your_github_username
GITHUB_API_TOKEN=your_github_token

# Server Configuration
HOST=0.0.0.0
PORT=$PORT  # Railway automatically sets this

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS Origins (Development only - production uses hardcoded domains)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### How to Set Environment Variables in Railway:

1. Go to your Railway project
2. Click on your backend service
3. Go to the **Variables** tab
4. Add each environment variable listed above
5. Make sure `ENVIRONMENT=production` is set

### Production Detection

The backend automatically detects production mode when:
- `ENVIRONMENT=production` environment variable is set
- This enables production CORS settings with your Vercel domain

## Environment Variables for Vercel (Frontend)

### Backend API URL

Set this in Vercel's environment variables:

```bash
VITE_API_URL=https://ai-charlotte-production.up.railway.app
```

### How to Set Environment Variables in Vercel:

1. Go to your Vercel project
2. Go to **Settings** → **Environment Variables**
3. Add `VITE_API_URL` with value: `https://ai-charlotte-production.up.railway.app`
4. Make sure to set it for **Production**, **Preview**, and **Development** environments

### Frontend Environment Detection

The frontend automatically detects the environment:
- **Development**: Uses Vite proxy (`/api` → `http://127.0.0.1:8000`)
- **Production**: Uses `VITE_API_URL` environment variable
- **Fallback**: Defaults to `https://ai-charlotte-production.up.railway.app` if `VITE_API_URL` is not set

## CORS Configuration

### Development
- Uses `CORS_ORIGINS` environment variable
- Default: `http://localhost:3000,http://localhost:5173`

### Production
- Hardcoded allowed origins:
  - `https://ai-charlotte-git-main-charlotteqazi-projects.vercel.app`
  - `https://charlotteqazi.co.uk`

## Health Check

Railway will automatically monitor your app using the health check endpoint:
- **URL**: `/health`
- **Response**: `{"status": "ok", "environment": "production"}`

## Deployment Process

1. **Push to GitHub**: Your code automatically deploys to both platforms
2. **Railway**: Deploys backend from root directory using `railway.json`
3. **Vercel**: Deploys frontend from `/frontend` directory
4. **Environment Variables**: Make sure all required variables are set in both platforms 