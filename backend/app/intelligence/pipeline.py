"""
Intelligence processing pipeline.

Orchestrates the flow: Feedback → Cleaner → Sentiment → Category → Priority.
"""

import logging
from dataclasses import dataclass, field

from app.intelligence.cleaner import TextCleaner
from app.intelligence.sentiment import SentimentAnalyzer, SentimentResult
from app.intelligence.categorizer import FeedbackCategorizer, CategoryResult
from app.intelligence.priority import PriorityScorer, PriorityResult

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Complete analysis result from the intelligence pipeline."""
    cleaned_text: str
    sentiment: SentimentResult
    category: CategoryResult
    priority: PriorityResult
    processing_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert analysis result to a dictionary for API response."""
        return {
            "cleaned_text": self.cleaned_text,
            "sentiment": {
                "label": self.sentiment.label,
                "score": self.sentiment.score,
                "confidence": self.sentiment.confidence,
                "positive_words": self.sentiment.positive_words,
                "negative_words": self.sentiment.negative_words,
            },
            "category": {
                "category": self.category.category,
                "confidence": self.category.confidence,
                "matched_keywords": self.category.matched_keywords,
            },
            "priority": {
                "priority": self.priority.priority,
                "score": self.priority.score,
                "reasons": self.priority.reasons,
            },
            "processing_steps": self.processing_steps,
        }


class IntelligencePipeline:
    """Orchestrates the full intelligence processing pipeline.

    Pipeline flow: Raw Text → Cleaner → Sentiment → Category → Priority
    """

    def __init__(self) -> None:
        self.cleaner = TextCleaner()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.categorizer = FeedbackCategorizer()
        self.priority_scorer = PriorityScorer()
        logger.info("Intelligence pipeline initialized.")

    def process(self, text: str, rating: int | None = None) -> AnalysisResult:
        """Run the full analysis pipeline on raw feedback text.

        Args:
            text: Raw feedback text from user.
            rating: Optional user rating (1-5) to factor into priority.

        Returns:
            AnalysisResult with sentiment, category, and priority.
        """
        steps: list[str] = []

        # Step 1: Clean text
        cleaned = self.cleaner.clean(text)
        steps.append("text_cleaning")
        logger.debug("Pipeline step 1 — Text cleaned.")

        # Step 2: Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(cleaned)
        steps.append("sentiment_analysis")
        logger.debug("Pipeline step 2 — Sentiment: %s (%.3f)", sentiment.label, sentiment.score)

        # Step 3: Auto-categorization
        category = self.categorizer.categorize(cleaned)
        steps.append("auto_categorization")
        logger.debug("Pipeline step 3 — Category: %s", category.category)

        # Step 4: Priority scoring (uses sentiment score + rating for context)
        priority = self.priority_scorer.score(
            cleaned,
            sentiment_score=sentiment.score,
            rating=rating,
        )
        steps.append("priority_scoring")
        logger.debug("Pipeline step 4 — Priority: %s (%.3f)", priority.priority, priority.score)

        result = AnalysisResult(
            cleaned_text=cleaned,
            sentiment=sentiment,
            category=category,
            priority=priority,
            processing_steps=steps,
        )
        logger.info(
            "Pipeline complete: sentiment=%s category=%s priority=%s",
            sentiment.label, category.category, priority.priority,
        )
        return result


# Module-level singleton
_pipeline: IntelligencePipeline | None = None


def get_pipeline() -> IntelligencePipeline:
    """Get or create the singleton pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = IntelligencePipeline()
    return _pipeline
