"""
AI Charlotte - Personal RAG Chatbot
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secure

from backend.api.routes import router
from backend.core.config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize security headers
secure_headers = secure.Secure.with_default_headers()

# Create FastAPI app
app = FastAPI(
    title="AI Charlotte RAG Backend",
    description="Personal RAG chatbot for Charlotte Qazi",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.is_production else [
        "https://ai-charlotte.vercel.app",
        "https://charlotteqazi.co.uk"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    await secure_headers.set_headers_async(response)
    return response

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/health")
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def health(request: Request) -> dict:
    """Health check endpoint with rate limiting."""
    return {"status": "ok", "environment": settings.environment} 