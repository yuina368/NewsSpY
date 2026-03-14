#!/usr/bin/env python3
"""
News fetcher: Fetch news from GNews API and yfinance
Optimized to fetch all company news in minimal API requests
"""

import requests
import yfinance as yf
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Set
from collections import defaultdict
from app.config import GNEWS_API_KEY, GNEWS_BASE_URL, NYSE_COMPANIES


# JST timezone (UTC+9)
JST = timezone(timedelta(hours=9))


class NewsAPIFetcher:
    """Fetch news from GNews API with smart multi-company matching"""

    def __init__(self):
        self.api_key = GNEWS_API_KEY
        self.base_url = GNEWS_BASE_URL

        # Build keyword map for efficient matching
        self.keyword_map = self._build_keyword_map()

    def _build_keyword_map(self) -> Dict[str, Set[str]]:
        """Build a mapping of keywords to tickers for efficient article classification"""
        keyword_map = defaultdict(set)

        for company in NYSE_COMPANIES:
            ticker = company["ticker"]
            name = company["name"]
            keywords = company.get("keywords", [])

            # Add ticker
            keyword_map[ticker.lower()].add(ticker)

            # Add company name words
            for word in name.split():
                if len(word) > 2:
                    keyword_map[word.lower()].add(ticker)

            # Add keywords
            for kw in keywords:
                for word in kw.split():
                    if len(word) > 2:
                        keyword_map[word.lower()].add(ticker)

        return dict(keyword_map)

    def _classify_article(self, title: str, content: str) -> Optional[str]:
        """
        Classify which company an article belongs to based on keywords

        Returns the ticker with the most keyword matches, or None if no match
        """
        text = f"{title} {content}".lower()
        words = re.findall(r'\b\w+\b', text)

        # Count matches for each ticker
        ticker_scores = defaultdict(int)

        for word in words:
            if word in self.keyword_map:
                for ticker in self.keyword_map[word]:
                    ticker_scores[ticker] += 1

        # Debug logging - show first few articles regardless of content
        if not hasattr(self, '_classify_log_count'):
            self._classify_log_count = 0
        if self._classify_log_count < 5 and title:
            print(f"    DEBUG CLASSIFY #{self._classify_log_count + 1}: {title[:60]}...")
            print(f"      Ticker scores: {dict(ticker_scores)}")
            print(f"      Sample words: {words[:15]}")
            self._classify_log_count += 1

        # Debug for specific companies
        if title and ("apple" in title.lower() or "tesla" in title.lower() or "microsoft" in title.lower() or "adobe" in title.lower() or "meta" in title.lower()):
            print(f"    DEBUG CLASSIFY (matched): {title[:60]}...")
            print(f"      Ticker scores: {dict(ticker_scores)}")

        # Return ticker with highest score
        if ticker_scores:
            return max(ticker_scores.items(), key=lambda x: x[1])[0]

        return None

    def _is_jst_trading_hours(self, published_at: str) -> bool:
        """
        Check if article was published during US trading hours
        This includes:
        1. JST 6:00-22:00 (pre-market and after-hours for current day)
        2. JST 23:30-6:00 (next day) for US market hours (9:30-16:00 ET)
        3. Articles from yesterday or today only

        Args:
            published_at: ISO format datetime string

        Returns:
            True if article was published during relevant trading hours
        """
        try:
            # Parse the published date
            if published_at.endswith('Z'):
                pub_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                pub_dt = datetime.fromisoformat(published_at)

            # Convert to JST
            pub_dt_jst = pub_dt.astimezone(JST)

            # Get current JST time
            now_jst = datetime.now(JST)

            # Check if article is from today, yesterday, or day before yesterday
            days_diff = (now_jst.date() - pub_dt_jst.date()).days

            # Only include articles from last 2 days (to cover weekends)
            if days_diff > 2:
                return False

            hour = pub_dt_jst.hour

            # Include if:
            # 1. JST 6:00-22:00 (pre-market through after-hours)
            # 2. JST 23:30-24:00 or 0:00-6:00 (US market hours 9:30-16:00 ET)
            in_range = (6 <= hour < 22) or (hour >= 23) or (hour < 6)

            # Debug logging for first few articles
            if not hasattr(self, '_log_count'):
                self._log_count = 0
            if self._log_count < 5:
                print(f"    DEBUG: Article time: {published_at} -> JST: {pub_dt_jst.strftime('%m-%d %H:%M')} (days_diff={days_diff}, hour={hour}, in_range={in_range})")
                self._log_count += 1

            return in_range

        except (ValueError, AttributeError):
            # If we can't parse the date, include it
            return True

    def _fetch_all_gnews_articles(self, max_articles: int = 100) -> List[Dict]:
        """
        Fetch all news articles in a single GNews API request
        by searching for all tickers with OR query
        """
        if not self.api_key:
            return []

        endpoint = f"{self.base_url}/search"

        # Build OR query with all tickers
        tickers = [c["ticker"] for c in NYSE_COMPANIES]
        # Use chunks to avoid query length limits
        ticker_groups = []
        chunk_size = 10

        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i + chunk_size]
            ticker_groups.append(" OR ".join(chunk))

        all_articles = []

        for i, query in enumerate(ticker_groups):
            params = {
                "q": query,
                "max": max_articles // len(ticker_groups) + 10,
                "lang": "en",
                "token": self.api_key
            }

            try:
                print(f"  [GNews] Fetching batch {i+1}/{len(ticker_groups)}...", end="")
                import time
                time.sleep(0.5)

                response = requests.get(endpoint, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                batch_articles = data.get("articles", [])
                all_articles.extend(batch_articles)
                print(f" {len(batch_articles)} articles")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f" Rate limit exceeded!")
                else:
                    print(f" Error: {e}")
            except Exception as e:
                print(f" Error: {str(e)[:50]}")

        return all_articles

    def _classify_and_distribute_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify articles by company and distribute them
        Only includes articles published during JST 6:00-22:00

        Returns: Dict mapping ticker to list of articles
        """
        classified = defaultdict(list)
        filtered_count = 0

        for article in articles:
            title = article.get("title", "")
            content = article.get("description", "") or article.get("content", "")
            published_at = article.get("publishedAt", "")

            if not title or title == "[Removed]":
                continue

            # Filter by JST trading hours (6:00-22:00)
            if not self._is_jst_trading_hours(published_at):
                filtered_count += 1
                continue

            # Classify the article
            ticker = self._classify_article(title, content)

            if ticker:
                classified[ticker].append({
                    "ticker": ticker,
                    "title": title,
                    "content": content or title,
                    "source": article.get("source", {}).get("name", "GNews"),
                    "source_url": article.get("url", ""),
                    "published_at": published_at
                })

        if filtered_count > 0:
            print(f"  Filtered {filtered_count} articles outside JST 6:00-22:00")

        # Debug: Print first few articles
        print(f"  DEBUG: Processing {len(articles)} articles")
        for i, article in enumerate(articles[:3]):
            print(f"  Article {i+1}: {article.get('title', 'N/A')[:80]}...")
            print(f"    Content preview: {article.get('description', article.get('content', 'N/A'))[:80]}...")

        return dict(classified)

    def get_articles(
        self,
        ticker: str,
        company_name: str,
        days: int = 30,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Fetch articles for a specific company
        Note: This method is kept for backward compatibility but uses cached results
        """

        # For single company request, use the batch fetcher approach
        articles = self._get_yfinance_articles(ticker, company_name)

        if not articles:
            from app.config import logger
            logger.warning(f"No articles found for {ticker}")

        return articles[:page_size]

    def fetch_all_companies(self) -> List[Dict]:
        """
        Fetch articles for all companies using yfinance (primary) + GNews (backup)
        Returns a flat list of all articles with ticker assigned
        """
        all_articles = []

        print(f"\n[Fetching News from Primary Sources (yfinance)]")
        print(f"  Companies: {len(NYSE_COMPANIES)}")

        # Step 1: Fetch from yfinance first (primary source for recent articles)
        yf_articles_by_ticker = {}
        total_yf = 0
        for company in NYSE_COMPANIES:
            ticker = company["ticker"]
            name = company["name"]
            yf_articles = self._get_yfinance_articles(ticker, name)
            if yf_articles:
                yf_articles_by_ticker[ticker] = yf_articles
                total_yf += len(yf_articles)
                if total_yf <= 20:  # Show first few
                    print(f"  {ticker}: {len(yf_articles)} articles")

        print(f"  Total from yfinance: {total_yf} articles")

        # Step 2: Add yfinance articles to main list
        for ticker, articles in yf_articles_by_ticker.items():
            all_articles.extend(articles)

        # Step 3: If no articles from yfinance, try GNews as backup
        if total_yf == 0:
            print(f"\n[No articles from yfinance, trying GNews API]")
            gnews_articles = self._fetch_all_gnews_articles(max_articles=100)

            print(f"\n[Classifying Articles from GNews]")
            classified = self._classify_and_distribute_articles(gnews_articles)

            print(f"  Classified {len(gnews_articles)} articles for {len(classified)} companies")

            # Convert to flat list
            for ticker, articles in classified.items():
                all_articles.extend(articles)
        else:
            print(f"\n[Using {total_yf} articles from yfinance (JST 6:00-22:00 filtered)]")

        print(f"\n[Total: {len(all_articles)} articles fetched]")
        return all_articles

    def _get_yfinance_articles(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch articles from yfinance (filtered to JST 6:00-22:00)"""
        try:
            ticker_obj = yf.Ticker(ticker)

            news = ticker_obj.news
            if not news:
                return []

            # Debug logging for first few tickers
            if not hasattr(self, '_yf_log_count'):
                self._yf_log_count = 0
            if self._yf_log_count < 3:
                print(f"    DEBUG yfinance {ticker}: {len(news)} raw articles")
                if news and len(news) > 0:
                    first_item = news[0]
                    provider_time = first_item.get("providerPublishTime", "")
                    if provider_time and isinstance(provider_time, (int, float)):
                        try:
                            pub_date = datetime.fromtimestamp(provider_time)
                            print(f"      First article time: {provider_time} -> {pub_date.isoformat()}")
                        except:
                            pass
                self._yf_log_count += 1

            articles = []
            for item in news:
                try:
                    provider = item.get("providerPublishTime", "")
                    source_name = item.get("publisher", "") or "Yahoo Finance"

                    if provider and isinstance(provider, (int, float)):
                        try:
                            pub_date = datetime.fromtimestamp(provider)
                        except (ValueError, TypeError, OSError):
                            pub_date = datetime.now()
                    else:
                        pub_date = datetime.now()

                    title = item.get("title", "")
                    if not title or title == "[Removed]":
                        continue

                    pub_iso = pub_date.isoformat()

                    # Filter by JST trading hours
                    if not self._is_jst_trading_hours(pub_iso):
                        continue

                    articles.append({
                        "ticker": ticker,
                        "title": title,
                        "content": item.get("summary", "") or title,
                        "source": source_name,
                        "source_url": item.get("link", ""),
                        "published_at": pub_iso
                    })
                except Exception:
                    continue

            return articles

        except Exception as e:
            return []
