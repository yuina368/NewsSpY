from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, date

from app.services.json_storage import (
    read_scores, read_companies, get_ticker_sentiment_history
)
from app.config import logger

router = APIRouter(tags=["scores"])


@router.get("/scores/ranking/{date_str}")
async def get_ranking(date_str: str, limit: int = 100, sentiment_filter: Optional[str] = None):
    """Get company ranking for a specific date (falls back to latest if date not found)"""
    logger.debug(f"get_ranking called with date_str: {date_str}, limit: {limit}, sentiment_filter: {sentiment_filter}")

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get all scores
    all_scores = read_scores()

    # Filter by date
    scores = [s for s in all_scores if s.get("date") == str(target_date)]

    # If no results for requested date, use latest available
    if not scores and all_scores:
        # Get latest date from scores
        dates = set(s.get("date") for s in all_scores if s.get("date"))
        if dates:
            latest_date = max(dates)
            logger.debug(f"No scores found for {target_date}, using latest date: {latest_date}")
            scores = [s for s in all_scores if s.get("date") == latest_date]

    # Filter by sentiment
    if sentiment_filter:
        if sentiment_filter == "positive":
            scores = [s for s in scores if s.get("score", 0) > 0]
        elif sentiment_filter == "negative":
            scores = [s for s in scores if s.get("score", 0) < 0]

    # Sort by rank and limit
    scores.sort(key=lambda x: x.get("rank", 999))
    scores = scores[:limit]

    # Get company names
    companies = read_companies()
    company_dict = {c["ticker"]: c["name"] for c in companies}

    # Build response
    results = []
    for score_item in scores:
        ticker = score_item.get("ticker")
        results.append({
            "company": {
                "id": ticker,  # Use ticker as id for JSON storage
                "ticker": ticker,
                "name": company_dict.get(ticker, ticker)
            },
            "score": score_item.get("score"),
            "article_count": score_item.get("article_count"),
            "avg_sentiment": score_item.get("avg_sentiment"),
            "rank": score_item.get("rank")
        })

    logger.debug(f"results count: {len(results)}")
    return results


@router.post("/scores/calculate/{date_str}")
async def calculate_scores(date_str: str):
    """Calculate scores for all companies on a specific date (no-op in JSON mode)"""
    # In JSON mode, scores are calculated during batch processing
    # This endpoint is kept for compatibility but does nothing
    return {
        "companies_scored": 0,
        "message": "In JSON mode, scores are calculated during batch processing. Use /api/batch/run instead."
    }


@router.get("/scores/company/{ticker}")
async def get_company_scores(ticker: str, days: int = 30):
    """Get score history for a specific company"""
    # Get sentiment history from JSON storage
    history_data = get_ticker_sentiment_history(ticker, days)

    results = []
    for item in history_data.get("history", []):
        results.append({
            "date": item["date"],
            "score": item["avg_score"],
            "article_count": item["article_count"],
            "avg_sentiment": item["avg_score"]
        })

    return results


@router.get("/scores/ticker/{ticker}/history")
async def get_ticker_sentiment_history(ticker: str, days: int = 30):
    """Get detailed sentiment history for a specific ticker"""
    return get_ticker_sentiment_history(ticker, days)
