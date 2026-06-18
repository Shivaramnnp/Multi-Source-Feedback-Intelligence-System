"""
Mock AI provider — built-in rule-based analysis engine.

Provides intelligent analysis without requiring external API keys.
Uses pattern matching, keyword analysis, and heuristics to generate
structured analysis results. This is the default provider.
"""

import logging
import time

from app.ai.base import AIProviderBase, AIResponse

logger = logging.getLogger(__name__)


class MockAIProvider(AIProviderBase):
    """Rule-based AI provider that generates analysis without external APIs.
    
    Uses keyword patterns and heuristics to provide meaningful analysis.
    Always available — no API keys required.
    """

    @property
    def name(self) -> str:
        return "mock"

    @property
    def display_name(self) -> str:
        return "Built-in Analysis Engine"

    @property
    def supported_models(self) -> list[str]:
        return ["rule-based-v1"]

    def is_configured(self) -> bool:
        return True  # Always available

    async def health_check(self) -> bool:
        return True

    async def analyze(
        self,
        feedback_text: str,
        rating: int,
        category: str,
        sentiment: str,
        priority: str,
        source: str,
    ) -> AIResponse:
        """Generate rule-based analysis."""
        start_time = time.perf_counter()
        text_lower = feedback_text.lower()

        summary = self._generate_summary(text_lower, rating, sentiment, category)
        root_cause = self._generate_root_cause(text_lower, category, sentiment)
        business_impact = self._generate_business_impact(rating, sentiment, priority, category)
        recommended_action = self._generate_recommended_action(category, priority, sentiment)
        priority_reason = self._generate_priority_reason(text_lower, rating, priority, sentiment)

        processing_time = (time.perf_counter() - start_time) * 1000
        confidence = self._calculate_confidence(text_lower, rating)

        result = AIResponse(
            summary=summary,
            root_cause=root_cause,
            business_impact=business_impact,
            recommended_action=recommended_action,
            priority_reason=priority_reason,
            confidence_score=confidence,
            provider=self.name,
            model_name="rule-based-v1",
            prompt_tokens="0",
            completion_tokens="0",
            processing_time_ms=round(processing_time, 2),
        )
        logger.info("Mock analysis complete in %.1fms, confidence=%.2f", processing_time, confidence)
        return result

    def _generate_summary(self, text: str, rating: int, sentiment: str, category: str) -> str:
        """Generate a contextual summary based on feedback signals."""
        if sentiment == "positive" and rating >= 4:
            if "feature" in text or "new" in text:
                return "Customer expresses strong satisfaction with recent feature additions, indicating successful product development aligned with user needs."
            if "support" in text or "help" in text or "team" in text:
                return "Customer highlights excellent support experience, reflecting positively on service quality and team responsiveness."
            return "Customer provides positive feedback with a high satisfaction rating, signaling strong product-market fit for their use case."
        
        if sentiment == "negative" and rating <= 2:
            if "crash" in text or "broken" in text or "bug" in text:
                return "Customer reports a critical technical issue causing service disruption, requiring immediate engineering attention."
            if "slow" in text or "performance" in text:
                return "Customer experiences significant performance degradation impacting their workflow and productivity."
            if "payment" in text or "billing" in text or "charge" in text:
                return "Customer raises a billing or payment concern that poses financial and trust implications."
            return "Customer expresses dissatisfaction with the product experience, indicating a risk of churn without intervention."
        
        if category == "feature":
            return "Customer suggests a product enhancement that could improve user experience and potentially drive adoption."
        if category == "bug":
            return "Customer reports a functional issue that degrades the expected product behavior and user experience."
        if category == "complaint":
            return "Customer expresses frustration with a specific aspect of the product or service requiring attention."
        
        return f"Customer provides {sentiment} feedback (rated {rating}/5) regarding their {category} experience via {text[:50]}..."

    def _generate_root_cause(self, text: str, category: str, sentiment: str) -> str:
        """Identify the root cause based on patterns."""
        causes = {
            "crash": "Application stability issue — likely an unhandled exception or memory leak in a critical code path.",
            "slow": "Performance bottleneck — potential causes include unoptimized database queries, missing indexes, or inadequate infrastructure scaling.",
            "bug": "Software defect in the application logic causing incorrect behavior or unexpected results.",
            "error": "Runtime error occurring during a user workflow, possibly due to edge case handling gaps or API contract violations.",
            "payment": "Payment processing failure — may stem from payment gateway integration issues, validation gaps, or currency handling errors.",
            "security": "Security concern identified — potential vulnerability in authentication, authorization, or data handling procedures.",
            "feature": "Product capability gap — current functionality does not meet user expectations or evolving market demands.",
            "confusing": "UX/UI design issue — the interface or workflow is not intuitive, leading to user confusion and reduced task completion rates.",
            "support": "Support process gap — user required assistance that should ideally be handled through self-service documentation or improved UX.",
        }

        for keyword, cause in causes.items():
            if keyword in text:
                return cause

        if sentiment == "negative":
            return "User experience falls short of expectations, suggesting a gap between promised value and delivered functionality."
        if category == "praise":
            return "Product delivers on core value proposition, meeting or exceeding user expectations in key workflows."
        return "Feedback stems from the user's direct experience with the product, reflecting their specific use case and expectations."

    def _generate_business_impact(self, rating: int, sentiment: str, priority: str, category: str) -> str:
        """Assess business impact."""
        if priority == "critical":
            return "CRITICAL: Immediate revenue and reputation risk. This issue likely affects multiple customers and could trigger churn, negative reviews, and support escalations if not resolved within 24 hours."
        if priority == "high":
            return "HIGH: Significant impact on user satisfaction and retention. Prolonged exposure to this issue will erode trust and may lead to increased support costs and competitive loss."
        if sentiment == "positive" and rating >= 4:
            return "POSITIVE: This feedback validates product direction and can be leveraged for testimonials, case studies, and feature promotion to drive acquisition."
        if category == "feature":
            return "MODERATE: Feature gaps can signal competitive pressure. Addressing this request could unlock new user segments and reduce churn from unmet needs."
        if rating <= 2:
            return "ELEVATED: Low satisfaction scores correlate with 3-5x higher churn probability. Without intervention, this customer segment is at risk of abandoning the product."
        return "MODERATE: This feedback contributes to overall product quality signals. Addressing it improves the aggregate user satisfaction score and NPS."

    def _generate_recommended_action(self, category: str, priority: str, sentiment: str) -> str:
        """Generate actionable recommendations."""
        if priority == "critical":
            return "Escalate immediately to the on-call engineering team. Create a P0 incident ticket, notify stakeholders, and provide the customer with a direct communication channel for status updates."
        if priority == "high":
            return "Create a high-priority ticket in the current sprint. Assign a senior engineer, set a 48-hour SLA for initial investigation, and proactively reach out to the customer with an acknowledgment."
        if sentiment == "positive":
            return "Send a personalized thank-you response. Flag this feedback for the marketing team as a potential testimonial. Share internally to reinforce successful product decisions."
        if category == "feature":
            return "Log as a feature request in the product backlog. Validate against existing roadmap priorities. If multiple users request this, consider bumping priority for the next planning cycle."
        if category == "bug":
            return "Create a bug ticket with reproduction steps. Assign to the relevant team lead for triage. Follow up with the customer once a fix is deployed."
        return "Acknowledge the feedback within 24 hours. Route to the appropriate team for review. Include in the next sprint retrospective for product improvement discussions."

    def _generate_priority_reason(self, text: str, rating: int, priority: str, sentiment: str) -> str:
        """Explain the priority assignment."""
        reasons = []

        urgent_keywords = ["critical", "broken", "security", "payment", "crash", "data loss"]
        found = [kw for kw in urgent_keywords if kw in text]
        if found:
            reasons.append(f"Contains urgent keywords: {', '.join(found)}")

        if rating <= 2:
            reasons.append(f"Very low user satisfaction rating ({rating}/5)")
        elif rating >= 4:
            reasons.append(f"High satisfaction rating ({rating}/5) — positive signal")

        if sentiment == "negative":
            reasons.append("Negative sentiment detected indicating user frustration")
        elif sentiment == "positive":
            reasons.append("Positive sentiment — lower urgency but high value for engagement")

        if not reasons:
            reasons.append("Standard feedback without urgent signals")

        return f"Priority '{priority}' assigned because: {'; '.join(reasons)}."

    def _calculate_confidence(self, text: str, rating: int) -> float:
        """Calculate confidence score based on available signals."""
        score = 0.5  # Base confidence

        # More text = more signals = higher confidence
        word_count = len(text.split())
        if word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1

        # Rating provides a clear signal
        if rating in (1, 2, 4, 5):
            score += 0.1
        
        # Strong keywords boost confidence
        strong_signals = ["crash", "broken", "love", "excellent", "terrible", "payment", "security"]
        if any(kw in text for kw in strong_signals):
            score += 0.1

        return round(min(score, 0.95), 2)
