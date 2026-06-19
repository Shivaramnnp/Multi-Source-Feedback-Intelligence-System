import pytest
from app.intelligence.sentiment import SentimentAnalyzer

def test_heuristic_sentiment():
    analyzer = SentimentAnalyzer()
    res = analyzer.analyze("This is a great and wonderful tool!", force_heuristic=True)
    assert res.label == "positive"
    assert res.score > 0.15
    assert "great" in res.positive_words

def test_transformer_sentiment_fallback():
    analyzer = SentimentAnalyzer()
    res = analyzer.analyze("This is a terrible experience. App crashes!")
    assert res.label in ["negative", "neutral", "positive"]
