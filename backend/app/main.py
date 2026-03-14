#!/usr/bin/env python3
"""
NewsSpY Backend API
FastAPI based backend for news sentiment analysis and company scoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime, date
from typing import List, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes.articles import router as articles_router
from app.routes.scores import router as scores_router
from app.routes.sentiments import router as sentiments_router
from app.routes.auth import router as auth_router
from app.routes.batch import router as batch_router
from app.database import DB_PATH, init_database, fetch_all_companies
from app.services.sentiment_analyzer import SentimentAnalyzer

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global sentiment analyzer instance
sentiment_analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for model loading"""
    global sentiment_analyzer
    
    # Startup
    print("🚀 Starting NewsSpY API...")
    print("📊 Initializing database...")
    init_database()
    
    print("🤖 Loading FinBERT model...")
    sentiment_analyzer = SentimentAnalyzer()
    print("✓ FinBERT model loaded successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down NewsSpY API...")

app = FastAPI(
    title="NewsSpY API",
    description="API for NYSE news sentiment analysis and company scoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Allow specific origins only for security
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(articles_router, prefix="/api")
app.include_router(scores_router, prefix="/api")
app.include_router(sentiments_router, prefix="/api")
app.include_router(batch_router, prefix="/api")

@app.get("/api/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": sentiment_analyzer is not None
    }

@app.get("/api/companies/")
async def get_companies():
    """Get all companies"""
    return fetch_all_companies()

@app.get("/api/model/status")
async def model_status():
    """Get FinBERT model status"""
    return {
        "loaded": sentiment_analyzer is not None,
        "model": "ProsusAI/finbert",
        "status": "ready" if sentiment_analyzer else "not loaded"
    }

