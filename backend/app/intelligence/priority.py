"""
Priority scorer for feedback.

Determines priority (low, medium, high, critical) based on urgent keywords,
sentiment score, and text analysis.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PriorityResult:
    """Result of priority scoring."""
    priority: str  # "low", "medium", "high", "critical"
    score: float  # 0.0 to 1.0
    reasons: list[str]


class PriorityScorer:
    """Determines feedback priority using keyword analysis and sentiment context."""

    URGENT_KEYWORDS: dict[str, float] = {
        "critical": 1.0,
        "broken": 0.8,
        "security": 1.0,
        "payment": 0.9,
        "crash": 0.9,
        "data loss": 1.0,
        "vulnerability": 1.0,
        "breach": 1.0,
        "exploit": 1.0,
        "unauthorized": 0.9,
        "emergency": 1.0,
        "urgent": 0.9,
        "asap": 0.8,
        "immediately": 0.8,
        "production down": 1.0,
        "outage": 1.0,
        "downtime": 0.9,
        "billing": 0.7,
        "charge": 0.6,
        "money": 0.7,
        "legal": 0.8,
        "compliance": 0.8,
        "gdpr": 0.9,
        "privacy": 0.8,
    }

    HIGH_KEYWORDS: dict[str, float] = {
        "bug": 0.6,
        "error": 0.5,
        "fail": 0.6,
        "failed": 0.6,
        "not working": 0.7,
        "does not work": 0.7,
        "unusable": 0.7,
        "blocker": 0.8,
        "blocking": 0.7,
        "regression": 0.7,
        "performance": 0.5,
        "slow": 0.4,
        "timeout": 0.6,
        "losing": 0.6,
        "lost": 0.5,
    }

    def score(self, text: str, sentiment_score: float = 0.0, rating: int | None = None) -> PriorityResult:
        """Score the priority of feedback text.

        Args:
            text: Cleaned feedback text.
            sentiment_score: Sentiment score from -1.0 to 1.0.
            rating: Optional user rating (1-5).
        """
        if not text:
            return PriorityResult(priority="low", score=0.0, reasons=["Empty text"])

        text_lower = text.lower()
        priority_score = 0.0
        reasons: list[str] = []

        # Check urgent keywords
        urgent_found = []
        for keyword, weight in self.URGENT_KEYWORDS.items():
            if keyword in text_lower:
                priority_score += weight
                urgent_found.append(keyword)
        if urgent_found:
            reasons.append(f"Urgent keywords: {', '.join(urgent_found)}")

        # Check high-priority keywords
        high_found = []
        for keyword, weight in self.HIGH_KEYWORDS.items():
            if keyword in text_lower:
                priority_score += weight * 0.6  # Weight less than urgent
                high_found.append(keyword)
        if high_found:
            reasons.append(f"High-priority keywords: {', '.join(high_found)}")

        # Factor in sentiment
        if sentiment_score < -0.5:
            priority_score += 0.4
            reasons.append(f"Strongly negative sentiment ({sentiment_score:.2f})")
        elif sentiment_score < -0.15:
            priority_score += 0.2
            reasons.append(f"Negative sentiment ({sentiment_score:.2f})")

        # Factor in rating
        if rating is not None:
            if rating == 1:
                priority_score += 0.5
                reasons.append("Lowest rating (1/5)")
            elif rating == 2:
                priority_score += 0.3
                reasons.append("Low rating (2/5)")

        # Normalize score to 0-1 range
        normalized = min(priority_score / 3.0, 1.0)

        # Determine priority level
        if normalized >= 0.7:
            priority = "critical"
        elif normalized >= 0.4:
            priority = "high"
        elif normalized >= 0.2:
            priority = "medium"
        else:
            priority = "low"
            if not reasons:
                reasons.append("No priority signals detected")

        result = PriorityResult(
            priority=priority,
            score=round(normalized, 3),
            reasons=reasons,
        )
        logger.info(
            "Priority scoring: priority=%s score=%.3f reasons=%s",
            result.priority, result.score, result.reasons,
        )
        return result
