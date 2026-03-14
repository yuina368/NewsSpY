#!/usr/bin/env python3
"""
JSON Storage Service - Simple file-based storage for NewsSpY
Stores articles and scores in JSON files, cleared on each update
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path

# Storage directory
STORAGE_DIR = Path("/app/data/json")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# File paths
ARTICLES_FILE = STORAGE_DIR / "articles.json"
SCORES_FILE = STORAGE_DIR / "scores.json"
COMPANIES_FILE = STORAGE_DIR / "companies.json"
STATUS_FILE = STORAGE_DIR / "status.json"


def clear_all_data() -> None:
    """Clear all JSON data files"""
    for file_path in [ARTICLES_FILE, SCORES_FILE, STATUS_FILE]:
        if file_path.exists():
            file_path.unlink()
    write_status({"last_updated": None, "articles_count": 0, "companies_count": 0})


def write_companies(companies: List[Dict]) -> None:
    """Write companies to JSON file"""
    with open(COMPANIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)


def read_companies() -> List[Dict]:
    """Read companies from JSON file"""
    if not COMPANIES_FILE.exists():
        return []
    with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_articles(articles: List[Dict]) -> None:
    """Write articles to JSON file (overwrites existing)"""
    with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def read_articles() -> List[Dict]:
    """Read articles from JSON file"""
    if not ARTICLES_FILE.exists():
        return []
    with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_scores(scores: List[Dict]) -> None:
    """Write scores to JSON file (overwrites existing)"""
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def read_scores() -> List[Dict]:
    """Read scores from JSON file"""
    if not SCORES_FILE.exists():
        return []
    with open(SCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_scores_for_date(target_date: date) -> List[Dict]:
    """Get scores for a specific date"""
    all_scores = read_scores()
    return [s for s in all_scores if s.get("date") == str(target_date)]


def get_articles_for_date(target_date: date) -> List[Dict]:
    """Get articles for a specific date"""
    all_articles = read_articles()
    target_str = str(target_date)
    return [a for a in all_articles if a.get("published_at", "").startswith(target_str)]


def get_ticker_sentiment_history(ticker: str, days: int = 30) -> Dict:
    """Get sentiment history for a specific ticker"""
    all_articles = read_articles()
    ticker_articles = [a for a in all_articles if a.get("ticker") == ticker]

    # Group by date
    from collections import defaultdict
    daily_data = defaultdict(lambda: {"scores": [], "count": 0})

    for article in ticker_articles:
        published_at = article.get("published_at", "")
        if published_at:
            date_str = published_at.split("T")[0]
            score = article.get("sentiment_score")
            if score is not None:
                daily_data[date_str]["scores"].append(score)
                daily_data[date_str]["count"] += 1

    # Calculate daily averages
    history = []
    for date_str, data in sorted(daily_data.items(), reverse=True)[:days]:
        scores = data["scores"]
        if scores:
            avg_score = sum(scores) / len(scores)
            positive = sum(1 for s in scores if s > 0)
            negative = sum(1 for s in scores if s < 0)
            neutral = sum(1 for s in scores if s == 0)
            total = len(scores)

            history.append({
                "date": date_str,
                "avg_score": avg_score,
                "article_count": total,
                "positive_pct": (positive / total) * 100,
                "negative_pct": (negative / total) * 100,
                "neutral_pct": (neutral / total) * 100
            })

    return {"history": history, "days": days}


def write_status(status: Dict) -> None:
    """Write status to JSON file"""
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def read_status() -> Dict:
    """Read status from JSON file"""
    if not STATUS_FILE.exists():
        return {"last_updated": None, "articles_count": 0, "companies_count": 0}
    with open(STATUS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def add_article(article: Dict) -> bool:
    """Add a single article (append to existing)"""
    articles = read_articles()
    articles.append(article)
    write_articles(articles)
    return True
