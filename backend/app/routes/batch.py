from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import logging

from app.database import init_database
from app.config import NYSE_COMPANIES
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.services.score_calculator import ScoreCalculator
from batch.news_fetcher import NewsAPIFetcher

logger = logging.getLogger(__name__)
router = APIRouter(tags=["batch"])

# Global task status
task_status: Dict[str, Dict[str, Any]] = {}


def run_batch_task(task_id: str):
    """Run batch processing in background"""
    try:
        task_status[task_id] = {
            "status": "running",
            "step": "initializing",
            "progress": 0,
            "message": "Starting batch processing...",
            "started_at": datetime.now().isoformat()
        }

        # 1. Initialize Database
        task_status[task_id]["step"] = "initializing_db"
        task_status[task_id]["progress"] = 10
        task_status[task_id]["message"] = "Initializing database..."
        init_database()

        # 2. Register Companies
        task_status[task_id]["step"] = "registering_companies"
        task_status[task_id]["progress"] = 20
        task_status[task_id]["message"] = "Registering companies..."
        from app.database import add_company, get_company_by_ticker
        companies_registered = 0
        for company in NYSE_COMPANIES:
            ticker = company["ticker"]
            name = company["name"]
            if not get_company_by_ticker(ticker):
                add_company(ticker, name)
            companies_registered += 1

        # 3. Fetch Articles
        task_status[task_id]["step"] = "fetching_articles"
        task_status[task_id]["progress"] = 40
        task_status[task_id]["message"] = "Fetching articles..."
        fetcher = NewsAPIFetcher()
        all_articles = fetcher.fetch_all_companies()

        # Group by ticker and save
        from collections import defaultdict
        from app.database import add_article
        import sqlite3
        from app.database import DB_PATH

        articles_by_ticker = defaultdict(list)
        for article in all_articles:
            ticker = article.get("ticker")
            if ticker:
                articles_by_ticker[ticker].append(article)

        articles_added = 0
        for ticker, articles in articles_by_ticker.items():
            company_id = get_company_by_ticker(ticker)
            if company_id:
                for article in articles:
                    success = add_article(
                        company_id=company_id,
                        title=article["title"],
                        content=article["content"],
                        source=article["source"],
                        source_url=article["source_url"],
                        published_at=article["published_at"]
                    )
                    if success:
                        articles_added += 1

        task_status[task_id]["articles_fetched"] = len(all_articles)
        task_status[task_id]["articles_added"] = articles_added

        # 4. Analyze Sentiment
        task_status[task_id]["step"] = "analyzing_sentiment"
        task_status[task_id]["progress"] = 60
        task_status[task_id]["message"] = f"Analyzing sentiment for {articles_added} articles..."

        analyzer = SentimentAnalyzer()
        from app.database import save_news_sentiment

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.title, a.content, a.published_at, c.ticker
            FROM articles a
            JOIN companies c ON a.company_id = c.id
            WHERE a.sentiment_score IS NULL
        """)
        articles = cursor.fetchall()
        cursor.close()
        conn.close()

        analyzed_count = 0
        for article_id, title, content, published_at, ticker in articles:
            try:
                text = f"{title} {content}"
                score, confidence = analyzer.analyze(text)

                if score > 0:
                    label = "positive"
                elif score < 0:
                    label = "negative"
                else:
                    label = "neutral"

                # Update article
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE articles
                    SET sentiment_score = ?, sentiment_confidence = ?
                    WHERE id = ?
                """, (score, confidence, article_id))
                conn.commit()
                cursor.close()
                conn.close()

                # Save sentiment
                save_news_sentiment(
                    ticker=ticker,
                    published_at=published_at,
                    sentiment_score=score,
                    label=label
                )
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error analyzing article {article_id}: {e}")

        task_status[task_id]["articles_analyzed"] = analyzed_count

        # 5. Calculate Scores
        task_status[task_id]["step"] = "calculating_scores"
        task_status[task_id]["progress"] = 80
        task_status[task_id]["message"] = "Calculating scores..."

        target_date = datetime.now().date()
        result = ScoreCalculator.calculate_for_date(target_date)

        from app.database import save_score
        scores_saved = 0
        scores_list = result.get("scores", [])
        for score_item in scores_list:
            ticker = score_item["ticker"]
            company_id = get_company_by_ticker(ticker)
            if company_id:
                success = save_score(
                    company_id=company_id,
                    date=target_date,
                    score=score_item["score"],
                    article_count=score_item["article_count"],
                    avg_sentiment=score_item["avg_sentiment"],
                    rank=score_item["rank"]
                )
                if success:
                    scores_saved += 1

        task_status[task_id]["step"] = "completed"
        task_status[task_id]["progress"] = 100
        task_status[task_id]["message"] = "Batch processing completed successfully"
        task_status[task_id]["completed_at"] = datetime.now().isoformat()
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["companies_registered"] = companies_registered
        task_status[task_id]["scores_saved"] = scores_saved

    except Exception as e:
        logger.exception("Batch processing failed")
        task_status[task_id]["status"] = "failed"
        task_status[task_id]["message"] = f"Error: {str(e)}"
        task_status[task_id]["completed_at"] = datetime.now().isoformat()


@router.post("/batch/run")
async def run_batch(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Start batch processing in background"""
    import uuid
    task_id = str(uuid.uuid4())

    background_tasks.add_task(run_batch_task, task_id)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Batch processing started in background"
    }


@router.get("/batch/status/{task_id}")
async def get_batch_status(task_id: str) -> Dict[str, Any]:
    """Get status of a batch task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_status[task_id]
