# backend/batch/news_fetcher.py（完全置き換え）

#!/usr/bin/env python3
"""
News fetcher: yfinance でニュースを取得し、
記事1件ごとに S&P500 銘柄を判定する設計。
"""

import re
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Set
from collections import defaultdict

from app.config import NYSE_COMPANIES

JST = timezone(timedelta(hours=9))


class NewsAPIFetcher:
    """
    記事単位で銘柄を判定するフェッチャー。
    - yfinance から各銘柄のニュースを取得
    - 記事ごとにキーワードスコアで銘柄を判定
    - 1記事が複数銘柄に関連する場合は最スコアの銘柄に割り当て
    """

    def __init__(self):
        # ticker → {keywords} の逆引きマップを構築
        self.companies       = NYSE_COMPANIES
        self.keyword_map     = self._build_keyword_map()
        self.ticker_set      = {c["ticker"] for c in self.companies}
        self._yf_log_count   = 0
        self._jst_log_count  = 0

    # ──────────────────────────────────────────
    # キーワードマップ構築
    # ──────────────────────────────────────────

    def _build_keyword_map(self) -> Dict[str, Set[str]]:
        """
        { "apple": {"AAPL"}, "iphone": {"AAPL"}, ... }
        1単語 → その単語を持つ銘柄の集合
        """
        keyword_map: Dict[str, Set[str]] = defaultdict(set)

        for company in self.companies:
            ticker   = company["ticker"]
            name     = company["name"]
            keywords = company.get("keywords", [])

            # ティッカー自体
            keyword_map[ticker.lower()].add(ticker)

            # 会社名の各単語（3文字以上）
            for word in re.findall(r"[A-Za-z]{3,}", name):
                keyword_map[word.lower()].add(ticker)

            # キーワードリスト
            for kw in keywords:
                for word in re.findall(r"[A-Za-z]{3,}", kw):
                    keyword_map[word.lower()].add(ticker)

        return dict(keyword_map)

    # ──────────────────────────────────────────
    # 記事1件 → 銘柄判定
    # ──────────────────────────────────────────

    def classify_article(self, title: str, content: str) -> Optional[str]:
        """
        記事のタイトル+本文から最もマッチする銘柄を返す。
        マッチなし → None
        """
        text  = f"{title} {content}".lower()
        words = re.findall(r"[a-z]{2,}", text)

        ticker_scores: Dict[str, int] = defaultdict(int)

        for word in words:
            if word in self.keyword_map:
                for ticker in self.keyword_map[word]:
                    ticker_scores[ticker] += 1

        if not ticker_scores:
            return None

        # スコア最大の銘柄を返す（同点の場合は先にヒットした方）
        best_ticker = max(ticker_scores, key=lambda t: ticker_scores[t])

        # スコアが1点のみ（偶然のヒット）は除外
        if ticker_scores[best_ticker] < 2:
            return None

        return best_ticker

    # ──────────────────────────────────────────
    # JST 時間フィルタ
    # ──────────────────────────────────────────

    def _is_jst_trading_hours(self, published_at: str) -> bool:
        """JST 06:00〜22:00 かつ直近2日以内の記事のみ通過"""
        try:
            pub_dt = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            ).astimezone(JST)

            now_jst   = datetime.now(JST)
            days_diff = (now_jst.date() - pub_dt.date()).days

            if days_diff > 2:
                return False

            return 6 <= pub_dt.hour < 22

        except (ValueError, AttributeError):
            return True

    # ──────────────────────────────────────────
    # yfinance からニュース取得
    # ──────────────────────────────────────────

    # backend/batch/news_fetcher.py の _fetch_yfinance メソッドのみ置き換え

    def _fetch_yfinance(self, ticker: str) -> List[Dict]:
        """
        yfinance 1.3.0 以降の新しいAPI構造に対応。
        news[i] = {'id': ..., 'content': { 'title', 'pubDate', 'summary', ... }}
        """
        try:
            raw_news = yf.Ticker(ticker).news or []
        except Exception:
            return []

        articles = []
        for item in raw_news:
            try:
                # 新構造: content の中に実データがある
                content = item.get("content", {})
                if not content:
                    continue

                title = content.get("title", "")
                if not title or title == "[Removed]":
                    continue

                # 公開日時: pubDate (ISO形式 "2026-05-01T20:44:36Z")
                pub_date_str = content.get("pubDate", "")
                if pub_date_str:
                    pub_iso = pub_date_str
                else:
                    pub_iso = datetime.now().isoformat()

                if not self._is_jst_trading_hours(pub_iso):
                    continue

                # 本文: summary または description
                body = (
                    content.get("summary", "")
                    or content.get("description", "")
                    or title
                )
                # HTMLタグを除去
                body = re.sub(r"<[^>]+>", "", body)

                # ソース名
                provider = content.get("provider", {})
                source_name = provider.get("displayName", "Yahoo Finance")

                # URL
                canonical = content.get("canonicalUrl", {})
                url = canonical.get("url", "")

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

    # ──────────────────────────────────────────
    # メインエントリーポイント
    # ──────────────────────────────────────────

    def fetch_all_companies(self) -> List[Dict]:
        """
        全銘柄のニュースを取得し、
        記事1件ごとに銘柄を判定して返す。

        フロー:
          1. 各銘柄の yfinance ニュースを取得（URLでdedup）
          2. 記事ごとに classify_article() で銘柄を判定
          3. 判定結果が yfinance 取得元と異なっても判定結果を優先
        """
        print(f"  対象銘柄数: {len(self.companies)}")

        # URL をキーにして重複を排除しながら収集
        seen_urls:    Set[str]  = set()
        raw_articles: List[Dict] = []

        for i, company in enumerate(self.companies):
            ticker = company["ticker"]
            fetched = self._fetch_yfinance(ticker)

            for article in fetched:
                url = article.get("source_url", "")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                # 取得元ティッカーを一時保存（分類のヒント）
                article["_source_ticker"] = ticker
                raw_articles.append(article)

            if (i + 1) % 50 == 0:
                print(f"    {i + 1}/{len(self.companies)} 銘柄取得完了 "
                      f"（記事数: {len(raw_articles)}）")

        print(f"  重複除去後の記事数: {len(raw_articles)}")

        # 記事ごとに銘柄を判定
        classified: List[Dict] = []
        unmatched  = 0

        for article in raw_articles:
            title   = article["title"]
            content = article["content"]

            ticker = self.classify_article(title, content)

            if ticker is None:
                # キーワードマッチなし → 取得元ティッカーをフォールバックとして使用
                ticker = article["_source_ticker"]

            classified.append({
                "ticker":       ticker,
                "title":        title,
                "content":      content,
                "source":       article["source"],
                "source_url":   article["source_url"],
                "published_at": article["published_at"],
            })

        print(f"  銘柄判定完了: {len(classified)} 記事")
        return classified