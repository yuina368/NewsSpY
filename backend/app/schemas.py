#!/usr/bin/env python3
"""
Pydantic Schemas: Data validation and serialization models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Company(BaseModel):
    """Company model"""
    id: int
    ticker: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Article(BaseModel):
    """Article model"""
    id: int
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_confidence: Optional[float] = None
    ticker: Optional[str] = None

    class Config:
        from_attributes = True


class ScoreResponse(BaseModel):
    """Score response model"""
    company: Company
    score: float
    article_count: int
    avg_sentiment: float
    rank: int


class RankingResponse(BaseModel):
    """Ranking response model"""
    company: Company
    score: float
    article_count: int
    avg_sentiment: float
    rank: int
    _actual_date: Optional[str] = None


class CompanyScore(BaseModel):
    """Company score history model"""
    date: str
    score: float
    article_count: int
    avg_sentiment: float


class SentimentHistory(BaseModel):
    """Sentiment history model"""
    date: str
    avg_score: float
    article_count: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
