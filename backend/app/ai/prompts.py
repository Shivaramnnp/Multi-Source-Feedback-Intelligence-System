"""
Prompt templates for AI analysis.

Centralized prompt management with versioning and structured output formatting.
"""

SYSTEM_PROMPT = """You are an expert feedback analyst for a software product company.
Your role is to analyze customer feedback and provide structured, actionable insights.
You must respond ONLY with valid JSON matching the exact schema specified.
Be concise, specific, and business-oriented in your analysis."""


ANALYSIS_PROMPT_TEMPLATE = """Analyze the following customer feedback and provide a structured analysis.

## Feedback Details
- **Text**: {feedback_text}
- **Rating**: {rating}/5
- **Category**: {category}
- **Sentiment**: {sentiment}
- **Priority**: {priority}
- **Source**: {source}

## Required Output (JSON)
Respond with ONLY a valid JSON object with these exact fields:
{{
  "summary": "A concise 1-2 sentence summary of what the customer is saying",
  "root_cause": "The underlying issue or motivation behind this feedback",
  "business_impact": "How this feedback impacts the business (revenue, retention, reputation, etc.)",
  "recommended_action": "Specific, actionable next step to address this feedback",
  "priority_reason": "Why this feedback has been assigned its priority level"
}}

Rules:
- Keep each field to 1-3 sentences maximum
- Be specific and actionable, not generic
- Consider the rating and sentiment when assessing impact
- If the feedback is positive, focus on how to leverage it
- If negative, focus on resolution and prevention
- The priority_reason should reference specific signals in the feedback"""


def build_analysis_prompt(
    feedback_text: str,
    rating: int,
    category: str,
    sentiment: str,
    priority: str,
    source: str,
) -> str:
    """Build the analysis prompt with feedback details filled in."""
    return ANALYSIS_PROMPT_TEMPLATE.format(
        feedback_text=feedback_text,
        rating=rating,
        category=category,
        sentiment=sentiment,
        priority=priority,
        source=source,
    )


# Version tracking for prompt iteration
PROMPT_VERSION = "1.0.0"
