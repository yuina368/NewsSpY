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

        # Return ticker with highest score
        if ticker_scores:
            return max(ticker_scores.items(), key=lambda x: x[1])[0]

        return None

    def _is_jst_trading_hours(self, published_at: str) -> bool:
        """
        Check if article was published during JST trading hours (6:00-22:00)
        This covers pre-market news before US market opens

        Args:
            published_at: ISO format datetime string

        Returns:
            True if article was published between 6:00-22:00 JST
        """
        try:
            # Parse the published date
            if published_at.endswith('Z'):
                pub_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                pub_dt = datetime.fromisoformat(published_at)

            # Convert to JST
            pub_dt_jst = pub_dt.astimezone(JST)

            # Check if between 6:00 and 22:00 JST
            hour = pub_dt_jst.hour
            return 6 <= hour < 22

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
            print(f"  Warning: No real articles found for {ticker}, using demo data", end="")
            articles = self._get_demo_articles(ticker, company_name)

        return articles[:page_size]

    def fetch_all_companies(self) -> List[Dict]:
        """
        Fetch articles for all companies using optimized batch approach
        Returns a flat list of all articles with ticker assigned
        """
        all_articles = []

        print(f"\n[Fetching News from GNews API]")
        print(f"  Companies: {len(NYSE_COMPANIES)}")

        # Step 1: Fetch all articles from GNews in batch
        gnews_articles = self._fetch_all_gnews_articles(max_articles=100)

        # Step 2: Classify and distribute articles
        print(f"\n[Classifying Articles]")
        classified = self._classify_and_distribute_articles(gnews_articles)

        print(f"  Classified {len(gnews_articles)} articles for {len(classified)} companies")

        # Step 3: Convert to flat list
        for ticker, articles in classified.items():
            all_articles.extend(articles)

        # Step 4: Fill gaps with yfinance for companies without articles
        companies_without_news = set(c["ticker"] for c in NYSE_COMPANIES) - set(classified.keys())

        if companies_without_news:
            print(f"\n[Filling gaps with yfinance for {len(companies_without_news)} companies]")
            for ticker in companies_without_news:
                company = next(c for c in NYSE_COMPANIES if c["ticker"] == ticker)
                yf_articles = self._get_yfinance_articles(ticker, company["name"])
                if yf_articles:
                    all_articles.extend(yf_articles)
                    print(f"  {ticker}: {len(yf_articles)} articles from yfinance")

        # Step 5: Fill remaining gaps with demo data
        companies_with_articles = set(a["ticker"] for a in all_articles)
        companies_still_missing = set(c["ticker"] for c in NYSE_COMPANIES) - companies_with_articles

        if companies_still_missing:
            print(f"\n[Using demo data for {len(companies_still_missing)} companies]")
            for ticker in companies_still_missing:
                company = next(c for c in NYSE_COMPANIES if c["ticker"] == ticker)
                demo_articles = self._get_demo_articles(ticker, company["name"])
                all_articles.extend(demo_articles)
                print(f"  {ticker}: {len(demo_articles)} demo articles")

        print(f"\n[Total: {len(all_articles)} articles fetched]")
        return all_articles

    def _get_yfinance_articles(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch articles from yfinance (filtered to JST 6:00-22:00)"""
        try:
            ticker_obj = yf.Ticker(ticker)

            news = ticker_obj.news
            if not news:
                return []

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

    def _get_demo_articles(self, ticker: str, name: str) -> List[Dict]:
        """Return demo articles for testing"""
        demo_articles = {
            "AAPL": [
                {"title": f"{name} Announces Revolutionary New Product Launch", "content": f"{name} has announced a groundbreaking new product that is expected to revolutionize the industry and drive significant revenue growth."},
                {"title": f"{name} Reports Record Quarterly Earnings, Beats Expectations", "content": f"{name}'s latest quarterly earnings exceeded analyst expectations by 15%, demonstrating strong operational efficiency and market leadership."},
                {"title": f"{name} Expands AI Capabilities with Major Investment", "content": f"{name} invests heavily in artificial intelligence research and development, positioning itself as a leader in AI innovation."},
                {"title": f"{name} Stock Reaches New All-Time High on Strong Performance", "content": f"{name} shares surge to record levels as investors respond positively to exceptional growth and profitability."},
            ],
            "MSFT": [
                {"title": f"{name} Cloud Services Show Strong Growth Momentum", "content": f"{name} Azure cloud services show exceptional growth in corporate sector, expanding market share significantly."},
                {"title": f"{name} Launches New Gaming Console with Overwhelming Demand", "content": f"{name} Xbox Series X2 receives overwhelming pre-orders, signaling strong consumer enthusiasm and revenue potential."},
                {"title": f"{name} Partners with OpenAI for Enterprise Solutions", "content": f"{name} deepens integration of ChatGPT into enterprise solutions, creating new revenue streams and competitive advantages."},
                {"title": f"{name} Reports Strong Q4 Results, Raises Guidance", "content": f"{name} delivers strong quarterly results and raises full-year guidance, reflecting confidence in continued growth."},
            ],
            "GOOGL": [
                {"title": f"{name} Launches Advanced AI Model with Superior Performance", "content": f"{name} Gemini AI shows superior performance in benchmark tests, establishing leadership in AI technology."},
                {"title": f"{name} Invests in Renewable Energy for Sustainable Growth", "content": f"{name} commits to 100% renewable energy by 2030, demonstrating commitment to sustainability and long-term value creation."},
                {"title": f"{name} Quantum Computing Breakthrough Opens New Opportunities", "content": f"{name} quantum chips demonstrate new computational capabilities, opening doors to revolutionary applications."},
                {"title": f"{name} Cloud Platform Shows Strong Adoption", "content": f"{name} Google Cloud continues to gain market share with strong enterprise adoption and revenue growth."},
            ],
            "AMZN": [
                {"title": f"{name} AWS Dominates Cloud Market with Strong Growth", "content": f"{name} Web Services maintains 32% market share in cloud computing with accelerating revenue growth."},
                {"title": f"{name} Expands Same-Day Delivery to 2,000 Cities", "content": f"{name} announces same-day delivery available in 2,000 cities, enhancing customer experience and competitive position."},
                {"title": f"{name} Acquires Healthcare Tech Startup for $1 Billion", "content": f"{name} invests in healthcare AI company for $1 billion, expanding into high-growth healthcare technology sector."},
                {"title": f"{name} E-commerce Platform Shows Strong Growth", "content": f"{name} online shopping volume grows 25% year-over-year, demonstrating strong market position and consumer demand."},
            ],
            "TSLA": [
                {"title": f"{name} Breaks Sales Records with Strong Demand", "content": f"{name} delivers record 1.8 million vehicles in record-breaking year, showing exceptional market demand."},
                {"title": f"{name} Stock Reaches All-Time High on Strong Performance", "content": f"{name} shares surge 45% on strong earnings report, reflecting investor confidence in growth prospects."},
                {"title": f"{name} Expands to India Market with New Facility", "content": f"{name} announces new manufacturing facility in India, positioning for significant growth in emerging markets."},
                {"title": f"{name} Battery Technology Breakthrough Improves Efficiency", "content": f"{name} announces major battery technology advancement, reducing costs and improving vehicle performance."},
            ],
            "META": [
                {"title": f"{name} Ad Revenue Shows Strong Recovery in Q4", "content": f"{name} advertising business shows strong recovery in Q4, demonstrating resilience and growth potential."},
                {"title": f"{name} AI Research Breakthrough Competes with GPT", "content": f"{name} releases advanced language model competing with GPT, establishing position in AI market."},
                {"title": f"{name} User Engagement Increases Across Platforms", "content": f"{name} reports strong user engagement growth across all platforms, driving advertising revenue growth."},
                {"title": f"{name} Expands E-commerce Integration", "content": f"{name} launches new e-commerce features across platforms, creating new revenue opportunities."},
            ],
            "NVDA": [
                {"title": f"{name} Dominates AI Chip Market with 300% Growth", "content": f"{name} GPU sales surge 300% due to AI demand, establishing market leadership and strong revenue growth."},
                {"title": f"{name} Stock Reaches $1 Trillion Valuation", "content": f"{name} becomes most valuable chipmaker in history, reflecting strong market position and growth prospects."},
                {"title": f"{name} Expands Data Center Business with New Solutions", "content": f"{name} announces new data center solutions for enterprise, expanding market opportunities."},
                {"title": f"{name} AI Software Platform Shows Strong Adoption", "content": f"{name} AI software platform gains strong enterprise adoption, creating recurring revenue streams."},
            ],
            "JPM": [
                {"title": f"{name} Posts Record Profits in Investment Banking", "content": f"{name} investment banking division reaches record revenue, demonstrating strong market position and execution."},
                {"title": f"{name} Launches New Wealth Management Platform", "content": f"{name} introduces AI-powered investment advisory for clients, expanding wealth management capabilities."},
                {"title": f"{name} Expands Cryptocurrency Trading Services", "content": f"{name} expands cryptocurrency trading services, positioning for growth in digital asset markets."},
                {"title": f"{name} Digital Banking Platform Shows Strong Growth", "content": f"{name} digital banking platform gains significant market share, driving customer acquisition and revenue growth."},
            ],
            "V": [
                {"title": f"{name} Payment Volume Increases to New High", "content": f"{name} credit card transaction volume reaches new high, showing strong consumer spending and market position."},
                {"title": f"{name} Expands B2B Solutions for Business Growth", "content": f"{name} launches new platform for business-to-business payments, expanding market opportunities."},
                {"title": f"{name} Reports Strong Q4 Earnings, Beats Expectations", "content": f"{name} earnings beat analyst expectations by 8%, demonstrating strong operational performance."},
                {"title": f"{name} Digital Wallet Adoption Accelerates", "content": f"{name} digital wallet platform shows strong adoption, driving transaction volume growth."},
            ],
            "WMT": [
                {"title": f"{name} Q4 Sales Surge with 6.5% Growth", "content": f"{name} holiday sales exceed expectations with 6.5% growth, showing strong consumer demand."},
                {"title": f"{name} E-commerce Platform Thrives with 25% Growth", "content": f"{name} online shopping volume grows 25% year-over-year, demonstrating successful digital transformation."},
                {"title": f"{name} Announces Sustainability Goals for Long-term Value", "content": f"{name} commits to carbon neutrality by 2040, positioning for sustainable growth and cost savings."},
                {"title": f"{name} Expands Market Share in Grocery Sector", "content": f"{name} gains market share in competitive grocery sector, showing strong operational execution."},
            ],
        }

        articles_data = demo_articles.get(ticker, [])
        articles = []

        # Generate demo articles with timestamps in JST 6:00-22:00
        now_jst = datetime.now(JST)
        current_hour = now_jst.hour

        # If current time is outside 6-22, adjust to 14:00 JST (middle of range)
        if current_hour < 6:
            base_time = now_jst.replace(hour=14, minute=0, second=0, microsecond=0)
        elif current_hour >= 22:
            base_time = now_jst.replace(hour=14, minute=0, second=0, microsecond=0)
        else:
            base_time = now_jst

        for i, article_data in enumerate(articles_data):
            # Spread articles throughout the day (every 2 hours)
            hours_ago = i * 2
            pub_time = base_time - timedelta(hours=hours_ago)

            # Ensure time stays within 6:00-22:00 JST
            pub_hour = pub_time.hour
            if pub_hour < 6:
                pub_time = pub_time.replace(hour=6 + (22 - 6 - pub_hour))
            elif pub_hour >= 22:
                pub_time = pub_time.replace(hour=6 + (pub_hour - 22))

            articles.append({
                "ticker": ticker,
                "title": article_data["title"],
                "content": article_data["content"],
                "source": "NewsSpY Demo Feed",
                "source_url": f"https://example.com/{ticker.lower()}-news-{i}",
                "published_at": pub_time.isoformat()
            })

        return articles
