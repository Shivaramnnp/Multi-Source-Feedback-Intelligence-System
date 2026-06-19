"""
Keyword-based sentiment analyzer.

Analyzes feedback text to determine sentiment (positive, neutral, negative)
using weighted keyword matching with intensity modifiers.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


_transformer_pipeline = None
_transformer_load_error = None


def get_transformer_pipeline():
    """Get the cached HuggingFace sentiment pipeline singleton with timeout protection."""
    global _transformer_pipeline, _transformer_load_error
    if _transformer_load_error is not None:
        return None
    if _transformer_pipeline is None:
        try:
            from transformers import pipeline
            import concurrent.futures
            logger.info("Initializing HuggingFace sentiment analyzer (distilbert-base-uncased-finetuned-sst-2-english)...")
            
            def load_model():
                return pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                )
            
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(load_model)
            try:
                _transformer_pipeline = future.result(timeout=10.0)  # Wait max 10 seconds for download/load
                logger.info("HuggingFace sentiment analyzer loaded successfully.")
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
                
        except Exception as e:
            import concurrent.futures
            if isinstance(e, concurrent.futures.TimeoutError):
                _transformer_load_error = "Model download/load timed out."
            else:
                _transformer_load_error = str(e)
            logger.error("Failed to load HuggingFace sentiment analyzer: %s. Falling back to heuristic model.", _transformer_load_error)
    return _transformer_pipeline


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    label: str  # "positive", "neutral", "negative"
    score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    positive_words: list[str] = field(default_factory=list)
    negative_words: list[str] = field(default_factory=list)


class SentimentAnalyzer:
    """HuggingFace & Keyword-based sentiment analysis engine."""

    POSITIVE_WORDS: dict[str, float] = {
        # Strong positive (weight 2.0)
        "excellent": 2.0, "amazing": 2.0, "outstanding": 2.0, "fantastic": 2.0,
        "incredible": 2.0, "exceptional": 2.0, "superb": 2.0, "brilliant": 2.0,
        "wonderful": 2.0, "perfect": 2.0, "love": 2.0, "best": 2.0,
        # Moderate positive (weight 1.5)
        "great": 1.5, "good": 1.5, "nice": 1.5, "helpful": 1.5,
        "impressive": 1.5, "pleased": 1.5, "satisfied": 1.5, "happy": 1.5,
        "enjoy": 1.5, "reliable": 1.5, "efficient": 1.5, "intuitive": 1.5,
        # Mild positive (weight 1.0)
        "fine": 1.0, "okay": 1.0, "decent": 1.0, "adequate": 1.0,
        "useful": 1.0, "works": 1.0, "like": 1.0, "smooth": 1.0,
        "fast": 1.0, "easy": 1.0, "clean": 1.0, "simple": 1.0,
        "improved": 1.0, "better": 1.0, "thanks": 1.0, "thank": 1.0,
        "appreciate": 1.5, "recommend": 1.5, "responsive": 1.0, "stable": 1.0,
    }

    NEGATIVE_WORDS: dict[str, float] = {
        # Strong negative (weight 2.0)
        "terrible": 2.0, "horrible": 2.0, "awful": 2.0, "worst": 2.0,
        "hate": 2.0, "disgusting": 2.0, "unacceptable": 2.0, "disaster": 2.0,
        "catastrophe": 2.0, "broken": 2.0, "crash": 2.0, "unusable": 2.0,
        # Moderate negative (weight 1.5)
        "bad": 1.5, "poor": 1.5, "slow": 1.5, "frustrating": 1.5,
        "annoying": 1.5, "disappointing": 1.5, "disappointed": 1.5, "difficult": 1.5,
        "confusing": 1.5, "complicated": 1.5, "unreliable": 1.5, "buggy": 1.5,
        "fail": 1.5, "failed": 1.5, "failure": 1.5, "error": 1.5,
        # Mild negative (weight 1.0)
        "issue": 1.0, "problem": 1.0, "concern": 1.0, "lacking": 1.0,
        "missing": 1.0, "unclear": 1.0, "inconsistent": 1.0, "lag": 1.0,
        "glitch": 1.0, "stuck": 1.0, "wrong": 1.0, "fix": 1.0,
        "complaint": 1.0, "worse": 1.5, "ugly": 1.0,
    }

    NEGATION_WORDS: set[str] = {
        "not", "no", "never", "neither", "nobody", "nothing",
        "nowhere", "nor", "cannot", "without", "hardly", "barely",
        "scarcely", "rarely", "seldom",
    }

    INTENSIFIERS: dict[str, float] = {
        "very": 1.5, "really": 1.5, "extremely": 2.0, "absolutely": 2.0,
        "incredibly": 2.0, "highly": 1.5, "totally": 1.5, "completely": 1.5,
        "so": 1.3, "quite": 1.2, "pretty": 1.2, "remarkably": 1.5,
        "super": 1.5, "utterly": 2.0,
    }

    def analyze(self, text: str, force_heuristic: bool = False) -> SentimentResult:
        """Analyze sentiment of cleaned text using HuggingFace DistilBERT with a heuristic fallback."""
        if not text:
            return SentimentResult(label="neutral", score=0.0, confidence=0.0)

        # 1. Run heuristic analyzer in background to collect matching positive/negative keyword lists
        heuristic_result = self._analyze_heuristic(text)

        if force_heuristic:
            return heuristic_result

        # 2. Try running HuggingFace Transformer model
        transformer = get_transformer_pipeline()
        if transformer is not None:
            try:
                # Truncate text to fit model max input length (512 tokens)
                truncated_text = " ".join(text.split()[:350])
                output = transformer(truncated_text)[0]
                label_raw = output["label"].upper()
                score_raw = float(output["score"])

                if label_raw == "POSITIVE":
                    label = "positive"
                    score = score_raw
                else:
                    label = "negative"
                    score = -score_raw

                result = SentimentResult(
                    label=label,
                    score=round(score, 3),
                    confidence=round(score_raw, 2),
                    positive_words=heuristic_result.positive_words,
                    negative_words=heuristic_result.negative_words,
                )
                logger.info(
                    "Transformer sentiment analysis: label=%s score=%.3f confidence=%.2f",
                    result.label, result.score, result.confidence,
                )
                return result
            except Exception as e:
                logger.error("HuggingFace sentiment analysis execution failed: %s. Falling back to heuristic.", str(e))

        return heuristic_result

    def _analyze_heuristic(self, text: str) -> SentimentResult:
        """Lexicon/keyword-based sentiment analysis fallback."""
        words = text.lower().split()
        positive_score = 0.0
        negative_score = 0.0
        found_positive: list[str] = []
        found_negative: list[str] = []
        total_words = len(words)

        i = 0
        while i < total_words:
            word = words[i]
            multiplier = 1.0

            # Check for negation in previous 3 words
            is_negated = False
            for j in range(max(0, i - 3), i):
                if words[j] in self.NEGATION_WORDS:
                    is_negated = True
                    break

            # Check for intensifier in previous word
            if i > 0 and words[i - 1] in self.INTENSIFIERS:
                multiplier = self.INTENSIFIERS[words[i - 1]]

            if word in self.POSITIVE_WORDS:
                weight = self.POSITIVE_WORDS[word] * multiplier
                if is_negated:
                    negative_score += weight * 0.75
                    found_negative.append(word)
                else:
                    positive_score += weight
                    found_positive.append(word)
            elif word in self.NEGATIVE_WORDS:
                weight = self.NEGATIVE_WORDS[word] * multiplier
                if is_negated:
                    positive_score += weight * 0.5
                    found_positive.append(word)
                else:
                    negative_score += weight
                    found_negative.append(word)

            i += 1

        # Calculate final score
        total_sentiment = positive_score + negative_score
        if total_sentiment == 0:
            score = 0.0
            confidence = 0.3
        else:
            score = (positive_score - negative_score) / total_sentiment
            coverage = min(total_sentiment / max(total_words * 0.3, 1), 1.0)
            confidence = round(0.4 + (coverage * 0.6), 2)

        # Determine label
        if score > 0.15:
            label = "positive"
        elif score < -0.15:
            label = "negative"
        else:
            label = "neutral"

        result = SentimentResult(
            label=label,
            score=round(score, 3),
            confidence=min(confidence, 1.0),
            positive_words=found_positive,
            negative_words=found_negative,
        )
        logger.debug(
            "Heuristic fallback analysis: label=%s score=%.3f confidence=%.2f pos=%s neg=%s",
            result.label, result.score, result.confidence,
            found_positive, found_negative,
        )
        return result

