#!/usr/bin/env python3

import re
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Set
from collections import defaultdict

from app.config import NYSE_COMPANIES

JST = timezone(timedelta(hours=9))


class NewsAPIFetcher:

    def __init__(self):
        self.companies   = NYSE_COMPANIES
        self.keyword_map = self._build_keyword_map()
        self.ticker_set  = {c["ticker"] for c in self.companies}

    def _build_keyword_map(self) -> Dict[str, Set[str]]:
        keyword_map: Dict[str, Set[str]] = defaultdict(set)
        for company in self.companies:
            ticker   = company["ticker"]
            name     = company["name"]
            keywords = company.get("keywords", [])
            keyword_map[ticker.lower()].add(ticker)
            for word in re.findall(r"[A-Za-z]{3,}", name):
                keyword_map[word.lower()].add(ticker)
            for kw in keywords:
                for word in re.findall(r"[A-Za-z]{3,}", kw):
                    keyword_map[word.lower()].add(ticker)
        return dict(keyword_map)

    def classify_article(self, title: str, content: str) -> Optional[str]:
        text  = f"{title} {content}".lower()
        words = re.findall(r"[a-z]{2,}", text)
        ticker_scores: Dict[str, int] = defaultdict(int)
        for word in words:
            if word in self.keyword_map:
                for ticker in self.keyword_map[word]:
                    ticker_scores[ticker] += 1
        if not ticker_scores:
            return None
        best = max(ticker_scores, key=lambda t: ticker_scores[t])
        if ticker_scores[best] < 2:
            return None
        return best

    def _get_last_market_close_utc(self) -> datetime:
        """
        直近の米国市場クローズ時刻をUTCで返す。
        平日: 当日または前日の21:00 UTC (ET 16:00)
        土曜: 金曜の21:00 UTC
        日曜: 金曜の21:00 UTC
        """
        ET = timezone(timedelta(hours=-4))  # EDT夏時間
        now_et = datetime.now(ET)

        # 当日16:00 ETを基準
        close_et = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

        # まだ当日クローズ前なら前日に戻す
        if now_et < close_et:
            close_et -= timedelta(days=1)

        # 土曜→金曜、日曜→金曜
        weekday = close_et.weekday()  # 0=月 4=金 5=土 6=日
        if weekday == 5:
            close_et -= timedelta(days=1)
        elif weekday == 6:
            close_et -= timedelta(days=2)

        return close_et.astimezone(timezone.utc)

    def _is_after_last_close(self, published_at: str) -> bool:
        """
        直近の米国市場クローズ以降の記事のみ通す。
        週末をまたぐ場合は金曜クローズ以降を取得。
        """
        try:
            pub_dt = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            ).astimezone(timezone.utc)

            last_close = self._get_last_market_close_utc()
            now_utc    = datetime.now(timezone.utc)

            return last_close <= pub_dt <= now_utc

        except (ValueError, AttributeError):
            return True

    def _fetch_yfinance(self, ticker: str) -> List[Dict]:
        try:
            raw_news = yf.Ticker(ticker).news or []
        except Exception:
            return []

        articles = []
        for item in raw_news:
            try:
                content = item.get("content", {})
                if not content:
                    continue

                title = content.get("title", "")
                if not title or title == "[Removed]":
                    continue

                pub_date_str = content.get("pubDate", "")
                pub_iso = pub_date_str if pub_date_str else datetime.now().isoformat()

                if not self._is_after_last_close(pub_iso):
                    continue

                body = (
                    content.get("summary", "")
                    or content.get("description", "")
                    or title
                )
                body = re.sub(r"<[^>]+>", "", body)

                provider    = content.get("provider", {})
                source_name = provider.get("displayName", "Yahoo Finance")
                canonical   = content.get("canonicalUrl", {})
                url         = canonical.get("url", "")

                articles.append({
                    "title":        title,
                    "content":      body,
                    "source":       source_name,
                    "source_url":   url,
                    "published_at": pub_iso,
                })
            except Exception:
                continue

        return articles

    def fetch_all_companies(self) -> List[Dict]:
        print(f"  対象銘柄数: {len(self.companies)}")

        seen_urls:    Set[str]   = set()
        raw_articles: List[Dict] = []

        for i, company in enumerate(self.companies):
            ticker  = company["ticker"]
            fetched = self._fetch_yfinance(ticker)

            for article in fetched:
                url = article.get("source_url", "")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                article["_source_ticker"] = ticker
                raw_articles.append(article)

            if (i + 1) % 50 == 0:
                print(f"    {i+1}/{len(self.companies)} 銘柄完了 "
                      f"（記事数: {len(raw_articles)}）")

        print(f"  重複除去後の記事数: {len(raw_articles)}")

        classified: List[Dict] = []
        for article in raw_articles:
            ticker = self.classify_article(article["title"], article["content"])
            if ticker is None:
                ticker = article["_source_ticker"]

            classified.append({
                "ticker":       ticker,
                "title":        article["title"],
                "content":      article["content"],
                "source":       article["source"],
                "source_url":   article["source_url"],
                "published_at": article["published_at"],
            })

        print(f"  銘柄判定完了: {len(classified)} 記事")
        return classified
