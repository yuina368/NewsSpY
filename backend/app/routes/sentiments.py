from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.json_storage import (
    read_articles, read_scores, read_companies, get_ticker_sentiment_history
)

router = APIRouter(tags=["sentiments"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/sentiments/daily")
@limiter.limit("10/minute")
async def get_daily_sentiments_api(
    request,
    target_date: Optional[str] = None,
    sentiment_filter: Optional[str] = None
):
    """
    Get today's sentiment scores for all companies (heatmap data)

    Parameters:
    - target_date: Optional date string in YYYY-MM-DD format. Defaults to today.
    - sentiment_filter: Optional filter for sentiment ('positive' or 'negative')

    Returns:
    - List of companies with average sentiment scores and article counts
    """
    try:
        if target_date:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            parsed_date = datetime.now().date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get scores for the date
    all_scores = read_scores()
    scores = [s for s in all_scores if s.get("date") == str(parsed_date)]

    # If no results, try latest date
    if not scores and all_scores:
        dates = set(s.get("date") for s in all_scores if s.get("date"))
        if dates:
            latest_date = max(dates)
            scores = [s for s in all_scores if s.get("date") == latest_date]
            parsed_date = datetime.strptime(latest_date, "%Y-%m-%d").date()

    # Get company names
    companies = read_companies()
    company_dict = {c["ticker"]: c["name"] for c in companies}

    # Build enriched sentiments
    enriched_sentiments = []
    for score_item in scores:
        ticker = score_item.get("ticker")
        enriched_sentiments.append({
            "ticker": ticker,
            "name": company_dict.get(ticker, ticker),
            "avg_score": score_item.get("score"),
            "article_count": score_item.get("article_count"),
            "date": str(parsed_date)
        })

    # Apply sentiment filter if provided
    if sentiment_filter:
        if sentiment_filter == "positive":
            enriched_sentiments = [s for s in enriched_sentiments if s["avg_score"] > 0]
        elif sentiment_filter == "negative":
            enriched_sentiments = [s for s in enriched_sentiments if s["avg_score"] < 0]

    return {
        "date": str(parsed_date),
        "count": len(enriched_sentiments),
        "sentiments": enriched_sentiments
    }


@router.get("/sentiments/{ticker}")
@limiter.limit("30/minute")
async def get_ticker_sentiment_history_api(
    request,
    ticker: str,
    days: int = 30
):
    """
    Get sentiment history for a specific ticker (chart data)

    Parameters:
    - ticker: Stock ticker symbol (e.g., AAPL)
    - days: Number of days to look back (default: 30)

    Returns:
    - Historical sentiment data for the ticker
    """
    # Validate ticker exists
    companies = read_companies()
    company_names = {c["ticker"]: c["name"] for c in companies}
    if ticker not in company_names:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    # Validate days parameter
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")

    history_data = get_ticker_sentiment_history(ticker, days)
    history = history_data.get("history", [])

    return {
        "ticker": ticker,
        "name": company_names.get(ticker, ticker),
        "days": days,
        "count": len(history),
        "history": history
    }


@router.get("/sentiments/summary")
@limiter.limit("5/minute")
async def get_sentiment_summary(request):
    """
    Get overall sentiment summary for today

    Returns:
    - Summary statistics including positive/negative/neutral counts
    """
    articles = read_articles()

    # Calculate statistics
    positive_count = sum(1 for a in articles if a.get("sentiment_score", 0) > 0)
    negative_count = sum(1 for a in articles if a.get("sentiment_score", 0) < 0)
    neutral_count = sum(1 for a in articles if a.get("sentiment_score", 0) == 0)

    total = len(articles)

    # Get top positive and negative tickers
    ticker_scores = {}
    for article in articles:
        ticker = article.get("ticker")
        score = article.get("sentiment_score")
        if ticker and score is not None:
            if ticker not in ticker_scores:
                ticker_scores[ticker] = {"scores": [], "count": 0}
            ticker_scores[ticker]["scores"].append(score)
            ticker_scores[ticker]["count"] += 1

    # Calculate average scores
    ticker_avg = {}
    for ticker, data in ticker_scores.items():
        if data["scores"]:
            avg = sum(data["scores"]) / len(data["scores"])
            ticker_avg[ticker] = {
                "avg_score": avg,
                "article_count": data["count"]
            }

    # Sort and get top 5
    top_positive = sorted(
        [{"ticker": t, **v} for t, v in ticker_avg.items() if v["avg_score"] > 0],
        key=lambda x: x["avg_score"],
        reverse=True
    )[:5]

    top_negative = sorted(
        [{"ticker": t, **v} for t, v in ticker_avg.items() if v["avg_score"] < 0],
        key=lambda x: x["avg_score"]
    )[:5]

    return {
        "date": datetime.now().date().isoformat(),
        "label_distribution": [
            {"label": "positive", "count": positive_count},
            {"label": "negative", "count": negative_count},
            {"label": "neutral", "count": neutral_count}
        ],
        "top_positive": top_positive,
        "top_negative": top_negative
    }
