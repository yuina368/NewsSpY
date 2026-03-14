from fastapi import APIRouter
from typing import Optional

from app.services.json_storage import read_articles

router = APIRouter(tags=["articles"])


@router.get("/articles/")
async def get_articles(
    ticker: Optional[str] = None,
    sentiment_filter: Optional[str] = None,
    limit: int = 50
):
    """Get articles with optional filters"""
    articles = read_articles()

    # Filter by ticker
    if ticker:
        articles = [a for a in articles if a.get("ticker") == ticker]

    # Filter by sentiment
    if sentiment_filter:
        if sentiment_filter == "positive":
            articles = [a for a in articles if a.get("sentiment_score", 0) > 0]
        elif sentiment_filter == "negative":
            articles = [a for a in articles if a.get("sentiment_score", 0) < 0]

    # Sort by published_at descending and limit
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    articles = articles[:limit]

    # Add id field for compatibility
    for i, article in enumerate(articles):
        article["id"] = i + 1

    return articles
