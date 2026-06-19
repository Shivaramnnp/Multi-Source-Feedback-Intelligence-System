"""
Keyword-based feedback auto-categorizer.

Classifies feedback into categories: bug, feature_request, praise, complaint, support.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CategoryResult:
    """Result of auto-categorization."""
    category: str
    confidence: float
    matched_keywords: list[str]


class FeedbackCategorizer:
    """Rule-based feedback categorizer using keyword matching."""

    CATEGORY_KEYWORDS: dict[str, dict[str, float]] = {
        "bug": {
            "bug": 3.0, "error": 2.5, "crash": 3.0, "broken": 2.5, "glitch": 2.5,
            "not working": 3.0, "does not work": 3.0, "failed": 2.0, "failure": 2.0,
            "freeze": 2.0, "freezing": 2.0, "stuck": 1.5, "unresponsive": 2.0,
            "exception": 2.5, "fault": 2.0, "defect": 3.0, "malfunction": 2.5,
            "issue": 1.5, "problem": 1.5, "incorrect": 1.5, "wrong": 1.5,
            "blank screen": 2.5, "white screen": 2.5, "500 error": 3.0,
            "404": 2.0, "timeout": 2.0, "data loss": 3.0, "corrupted": 2.5,
        },
        "feature_request": {
            "feature": 3.0, "request": 2.0, "add": 1.5, "implement": 2.5,
            "would be nice": 2.5, "wish": 2.0, "suggest": 2.5, "suggestion": 2.5,
            "could you": 2.0, "can you": 1.5, "please add": 3.0, "need": 1.5,
            "want": 1.5, "should have": 2.0, "would like": 2.5, "missing feature": 3.0,
            "new feature": 3.0, "enhancement": 2.5, "improve": 2.0, "improvement": 2.0,
            "integrate": 2.0, "integration": 2.0, "support for": 2.0,
            "capability": 2.0, "functionality": 2.0, "option": 1.5,
        },
        "praise": {
            "love": 3.0, "great": 2.5, "excellent": 3.0, "amazing": 3.0,
            "awesome": 3.0, "fantastic": 3.0, "wonderful": 3.0, "perfect": 3.0,
            "best": 2.5, "thank": 2.0, "thanks": 2.0, "appreciate": 2.5,
            "impressed": 2.5, "outstanding": 3.0, "superb": 3.0, "brilliant": 3.0,
            "well done": 3.0, "good job": 3.0, "nice work": 2.5, "keep up": 2.0,
            "satisfied": 2.0, "happy": 2.0, "pleased": 2.0, "enjoy": 2.0,
            "recommend": 2.5, "beautiful": 2.0, "intuitive": 2.0, "smooth": 1.5,
        },
        "complaint": {
            "complaint": 3.0, "complain": 3.0, "unhappy": 2.5, "dissatisfied": 2.5,
            "frustrating": 2.5, "frustrated": 2.5, "annoying": 2.0, "annoyed": 2.0,
            "terrible": 3.0, "horrible": 3.0, "awful": 3.0, "worst": 3.0,
            "hate": 2.5, "unacceptable": 3.0, "ridiculous": 2.5, "waste": 2.0,
            "poor": 2.0, "bad": 1.5, "slow": 1.5, "disappointing": 2.5,
            "disappointed": 2.5, "unusable": 3.0, "pathetic": 3.0,
            "refund": 2.5, "cancel": 2.0, "subscription": 1.5, "overpriced": 2.5,
        },
        "support": {
            "help": 2.5, "how to": 3.0, "how do": 2.5, "cannot": 1.5,
            "unable": 2.0, "assist": 2.5, "assistance": 2.5, "support": 2.5,
            "guide": 2.0, "tutorial": 2.5, "documentation": 2.0, "docs": 1.5,
            "instructions": 2.0, "steps": 1.5, "configure": 2.0, "setup": 2.0,
            "install": 2.0, "installation": 2.0, "account": 1.5, "password": 2.0,
            "login": 1.5, "access": 1.5, "permission": 1.5, "reset": 1.5,
            "where is": 2.0, "what is": 1.5, "explain": 2.0,
        },
    }

    def categorize(self, text: str, corrections: list = None) -> CategoryResult:
        """Categorize cleaned feedback text, optionally adjusting weights based on session corrections."""
        if not text:
            return CategoryResult(category="support", confidence=0.0, matched_keywords=[])

        text_lower = text.lower()

        # 1. First run: Calculate base scores using static keyword weights
        base_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0.0
            for keyword, weight in keywords.items():
                if keyword in text_lower:
                    score += weight
            base_scores[category] = score

        base_best_category = max(base_scores, key=base_scores.get) if any(base_scores.values()) else "support"

        # 2. Adjust keywords weights using corrections list
        import copy
        keywords_map = copy.deepcopy(self.CATEGORY_KEYWORDS)

        adjustments_applied = 0
        if corrections:
            db_to_pipeline = {
                "bug": "bug",
                "feature": "feature_request",
                "praise": "praise",
                "complaint": "complaint",
                "other": "support"
            }
            for corr, fb_text in corrections:
                if corr.field_corrected != "category":
                    continue
                
                corr_clean = fb_text.lower()
                old_cat = db_to_pipeline.get(corr.old_value, corr.old_value)
                new_cat = db_to_pipeline.get(corr.new_value, corr.new_value)

                # If there are keywords in the corrected text, boost them
                if new_cat in keywords_map:
                    for kw in keywords_map[new_cat]:
                        if kw in corr_clean and kw in text_lower:
                            keywords_map[new_cat][kw] += 0.75  # Boost weight
                            adjustments_applied += 1
                
                # Penalize keywords from the incorrect category that are in the corrected text
                if old_cat in keywords_map:
                    for kw in keywords_map[old_cat]:
                        if kw in corr_clean and kw in text_lower:
                            keywords_map[old_cat][kw] = max(0.0, keywords_map[old_cat][kw] - 0.75)  # Penalize weight
                            adjustments_applied += 1

        # 3. Second run: Calculate adjusted scores using the modified keywords map
        scores = {}
        matches = {}
        for category, keywords in keywords_map.items():
            score = 0.0
            matched = []
            for keyword, weight in keywords.items():
                if keyword in text_lower:
                    score += weight
                    matched.append(keyword)
            scores[category] = score
            matches[category] = matched

        best_category = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best_category]
        total_score = sum(scores.values())

        if best_score == 0:
            result = CategoryResult(category="support", confidence=0.3, matched_keywords=[])
        else:
            confidence = round(min(best_score / max(total_score, 1) + 0.2, 1.0), 2)
            result = CategoryResult(
                category=best_category,
                confidence=confidence,
                matched_keywords=matches[best_category],
            )

        if adjustments_applied > 0:
            if base_best_category != best_category:
                logger.info(
                    "Learning Loop: category adjusted from '%s' to '%s' (adjustments=%d)",
                    base_best_category, best_category, adjustments_applied
                )
            else:
                logger.debug(
                    "Learning Loop: keyword weights adjusted but category remained '%s' (adjustments=%d)",
                    best_category, adjustments_applied
                )

        return result

