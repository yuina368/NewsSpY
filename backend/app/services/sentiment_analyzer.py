#!/usr/bin/env python3
from typing import Tuple
from transformers import pipeline

class SentimentAnalyzer:

    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert"
        )

    def analyze(self, text: str) -> Tuple[float, float]:
        """
        Analyze sentiment using FinBERT model only.

        Returns:
            Tuple[float, float]: (sentiment_score, confidence)
            - sentiment_score: positive score (>0), negative score (<0), neutral (0)
            - confidence: model confidence level
        """
        if not text:
            return 0.0, 0.0

        result = self.classifier(text[:512])[0]
        label = result["label"]  # positive / negative / neutral
        confidence = result["score"]

        if label == "positive":
            score = confidence
        elif label == "negative":
            score = -confidence
        else:  # neutral
            score = 0.0

        return score, confidence

    def analyze_batch(self, texts: list) -> list:
        results = []
        for text in texts:
            score, confidence = self.analyze(text)
            results.append({
                "sentiment_score": score,
                "sentiment_confidence": confidence
            })
        return results
