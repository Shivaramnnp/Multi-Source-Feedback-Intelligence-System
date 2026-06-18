"""
TypedDict schema defining the LangGraph execution state for feedback processing.
"""

from typing import Any, Dict, List, TypedDict


class FeedbackAgentState(TypedDict):
    # Raw Inputs
    raw_text: str
    rating: int
    source: str

    # DB records
    feedback_id: str | None
    cleaned_text: str | None

    # Analysis
    category: str | None
    sentiment: str | None
    priority: str | None

    # Trend intelligence
    is_spike: bool | None
    is_churn_risk: bool | None
    recurring_pattern: str | None

    # Actions triggered
    actions_triggered: List[str]
    slack_alert_sent: bool | None
    jira_ticket_key: str | None

    # Learning outputs
    learning_notes: str | None

    # Execution logs
    agent_logs: List[str]
