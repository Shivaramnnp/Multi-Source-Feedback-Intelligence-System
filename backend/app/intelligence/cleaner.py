"""
Text cleaner for the intelligence pipeline.

Normalizes and sanitizes raw feedback text before NLP analysis.
"""

import re
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans and normalizes raw feedback text for NLP processing."""

    # Common contractions mapping
    CONTRACTIONS: dict[str, str] = {
        "can't": "cannot",
        "won't": "will not",
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "hasn't": "has not",
        "haven't": "have not",
        "hadn't": "had not",
        "couldn't": "could not",
        "wouldn't": "would not",
        "shouldn't": "should not",
        "i'm": "i am",
        "you're": "you are",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "they're": "they are",
        "i've": "i have",
        "you've": "you have",
        "we've": "we have",
        "they've": "they have",
        "i'll": "i will",
        "you'll": "you will",
        "he'll": "he will",
        "she'll": "she will",
        "we'll": "we will",
        "they'll": "they will",
        "i'd": "i would",
        "you'd": "you would",
        "he'd": "he would",
        "she'd": "she would",
        "we'd": "we would",
        "they'd": "they would",
    }

    @staticmethod
    def clean(text: str) -> str:
        """Clean and normalize feedback text.

        Steps:
        1. Strip leading/trailing whitespace
        2. Lowercase
        3. Expand contractions
        4. Remove URLs
        5. Remove email addresses
        6. Remove special characters (keep letters, numbers, spaces, basic punctuation)
        7. Collapse multiple spaces
        """
        if not text or not text.strip():
            return ""

        cleaned = text.strip()
        cleaned = cleaned.lower()

        # Expand contractions
        for contraction, expansion in TextCleaner.CONTRACTIONS.items():
            cleaned = cleaned.replace(contraction, expansion)

        # Remove URLs
        cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned)

        # Remove email addresses
        cleaned = re.sub(r"\S+@\S+\.\S+", "", cleaned)

        # Remove special chars but keep letters, numbers, spaces, and basic punctuation
        cleaned = re.sub(r"[^a-z0-9\s.,!?;:'-]", " ", cleaned)

        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        logger.debug("Cleaned text: '%s' -> '%s'", text[:50], cleaned[:50])
        return cleaned
