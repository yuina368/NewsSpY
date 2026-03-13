#!/usr/bin/env python3
"""
Config: Application configuration
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Logging setup
def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# NewsAPI (deprecated - requires paid plan)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "demo")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# GNews API (free tier: 100 requests/day)
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
GNEWS_BASE_URL = "https://gnews.io/api/v4"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "newspy.db")

# Load companies from JSON file
def load_companies():
    """Load companies from companies.json file"""
    companies_file = Path(__file__).parent.parent / "companies.json"
    
    if companies_file.exists():
        with open(companies_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Fallback to hardcoded list if file doesn't exist
        return [
            {"ticker": "AAPL", "name": "Apple Inc.", "keywords": ["Apple", "iPhone"]},
            {"ticker": "MSFT", "name": "Microsoft Corporation", "keywords": ["Microsoft", "Windows"]},
            {"ticker": "GOOGL", "name": "Alphabet Inc.", "keywords": ["Google", "Alphabet"]},
            {"ticker": "AMZN", "name": "Amazon.com Inc.", "keywords": ["Amazon", "AWS"]},
            {"ticker": "TSLA", "name": "Tesla Inc.", "keywords": ["Tesla", "Elon Musk"]},
        ]

NYSE_COMPANIES = load_companies()

# Sentiment Analysis
SENTIMENT_THRESHOLD_POSITIVE = 0.05
SENTIMENT_THRESHOLD_NEGATIVE = -0.05
