#!/usr/bin/env python3
"""
NewsSpY Batch Processing - JSON-based version
手動実行: python batch_process.py
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict

# JST timezone (UTC+9)
JST = timezone(timedelta(hours=9))

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import NYSE_COMPANIES
from app.services.json_storage import (
    clear_all_data, write_companies, write_articles, write_scores,
    write_status, add_article, get_ticker_sentiment_history
)
from app.services.sentiment_analyzer import SentimentAnalyzer
from batch.news_fetcher import NewsAPIFetcher

# Time decay calculator
class TimeDecayCalculator:
    """Calculate time-decay scores for news sentiment"""

    @staticmethod
    def calculate_decay_score(sentiment_score: float, published_at: str) -> float:
        """
        Apply time decay to sentiment score
        - Within 6 hours: 1.0 (full weight)
        - 6-24 hours: 0.8
        - 24-48 hours: 0.5
        - 48+ hours: 0.2
        """
        try:
            if published_at.endswith('Z'):
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                pub_time = datetime.fromisoformat(published_at)

            current_time = datetime.now(pub_time.tzinfo)
            time_diff = current_time - pub_time
            hours_ago = time_diff.total_seconds() / 3600

            # More lenient time decay
            if hours_ago < 6:
                time_decay = 1.0
            elif hours_ago < 24:
                time_decay = 0.8
            elif hours_ago < 48:
                time_decay = 0.5
            else:
                time_decay = 0.2

            return sentiment_score * time_decay
        except:
            return sentiment_score


class NewsSpYBatchProcessor:
    """メインバッチプロセッサ - JSONベース"""

    def __init__(self):
        self.fetcher = NewsAPIFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.time_decay_calc = TimeDecayCalculator()
        self.companies_count = 0
        self.articles_count = 0
        self.analyzed_count = 0

    def run(self):
        """メインプロセス実行"""
        print("=" * 60)
        print("  🚀 NewsSpY Batch Processing Start (JSON Mode)")
        print("=" * 60)
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  JST Time: {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 0. Clear all data
        print("[0/5] Clearing old data...")
        clear_all_data()
        print("      ✓ Old data cleared")
        print()

        # 1. Save Companies
        print("[1/5] Saving Companies...")
        companies_list = [{"ticker": c["ticker"], "name": c["name"]} for c in NYSE_COMPANIES]
        write_companies(companies_list)
        self.companies_count = len(companies_list)
        print(f"      ✓ {self.companies_count} companies saved")
        print()

        # 2. Fetch Articles
        print("[2/5] Fetching Articles from GNews API...")
        all_articles = self.fetcher.fetch_all_companies()
        self.articles_count = len(all_articles)

        # Group by ticker
        articles_by_ticker = defaultdict(list)
        for article in all_articles:
            ticker = article.get("ticker")
            if ticker:
                articles_by_ticker[ticker].append(article)

        # Save articles to JSON
        articles_to_save = []
        for article in all_articles:
            articles_to_save.append({
                "ticker": article["ticker"],
                "title": article["title"],
                "content": article["content"],
                "source": article["source"],
                "source_url": article["source_url"],
                "published_at": article["published_at"],
                "sentiment_score": None,  # Will be filled later
                "sentiment_confidence": None
            })

        write_articles(articles_to_save)

        # Show statistics
        ticker_counts = {ticker: len(articles) for ticker, articles in articles_by_ticker.items()}
        print(f"      ✓ {self.articles_count} articles fetched (JST 6:00-22:00 only)")
        print(f"      Top tickers:")
        for ticker, count in sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"        {ticker}: {count} articles")
        print()

        # 3. Analyze Sentiment
        print("[3/5] Analyzing Sentiment...")
        articles_with_sentiment = []
        for article in articles_to_save:
            try:
                text = f"{article['title']} {article['content']}"
                score, confidence = self.sentiment_analyzer.analyze(text)

                article["sentiment_score"] = score
                article["sentiment_confidence"] = confidence
                articles_with_sentiment.append(article)
                self.analyzed_count += 1

                if self.analyzed_count % 10 == 0:
                    print(f"      Analyzed {self.analyzed_count}/{self.articles_count} articles...")
            except Exception as e:
                print(f"      Error analyzing article: {e}")
                # Still include article without sentiment
                articles_with_sentiment.append(article)

        # Update articles with sentiment scores
        write_articles(articles_with_sentiment)
        print(f"      ✓ {self.analyzed_count} articles analyzed")
        print()

        # 4. Calculate Scores
        print("[4/5] Calculating Scores...")
        target_date = datetime.now().date()

        # Group by ticker and calculate scores
        ticker_scores = {}
        for article in articles_with_sentiment:
            ticker = article["ticker"]
            sentiment_score = article.get("sentiment_score")

            if sentiment_score is not None:
                # Apply time decay
                decayed_score = self.time_decay_calc.calculate_decay_score(
                    sentiment_score,
                    article["published_at"]
                )

                if ticker not in ticker_scores:
                    ticker_scores[ticker] = {
                        "ticker": ticker,
                        "scores": [],
                        "article_count": 0,
                        "avg_sentiment": 0
                    }

                ticker_scores[ticker]["scores"].append(decayed_score)
                ticker_scores[ticker]["article_count"] += 1

        # Calculate final scores
        scores_list = []
        for ticker, data in ticker_scores.items():
            if data["scores"]:
                avg_score = sum(data["scores"]) / len(data["scores"])

                # Calculate average sentiment (without decay for display)
                articles_for_ticker = [a for a in articles_with_sentiment if a["ticker"] == ticker]
                sentiments = [a["sentiment_score"] for a in articles_for_ticker if a.get("sentiment_score") is not None]
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

                scores_list.append({
                    "ticker": ticker,
                    "date": str(target_date),
                    "score": avg_score,
                    "article_count": data["article_count"],
                    "avg_sentiment": avg_sentiment
                })

        # Sort by score and assign ranks
        scores_list.sort(key=lambda x: x["score"], reverse=True)
        for rank, item in enumerate(scores_list, 1):
            item["rank"] = rank

        # Save scores
        write_scores(scores_list)

        print(f"      ✓ Scores calculated for {len(scores_list)} companies")
        print(f"      Top 5:")
        for item in scores_list[:5]:
            print(f"        Rank {item['rank']}: {item['ticker']} = {item['score']:.3f} ({item['article_count']} articles)")
        print()

        # 5. Update Status
        print("[5/5] Updating Status...")
        status = {
            "last_updated": datetime.now().isoformat(),
            "last_updated_jst": datetime.now(JST).isoformat(),
            "articles_count": self.articles_count,
            "companies_count": self.companies_count,
            "analyzed_count": self.analyzed_count,
            "scores_count": len(scores_list)
        }
        write_status(status)
        print(f"      ✓ Status updated")
        print()

        print("=" * 60)
        print("  ✓ Batch Processing Complete!")
        print(f"  Articles: {self.articles_count}")
        print(f"  Analyzed: {self.analyzed_count}")
        print(f"  Companies: {len(scores_list)}")
        print("=" * 60)
        print()


if __name__ == "__main__":
    processor = NewsSpYBatchProcessor()
    processor.run()
