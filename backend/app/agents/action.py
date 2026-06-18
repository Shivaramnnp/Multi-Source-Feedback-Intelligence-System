"""
Action Agent node.

Dispatches mock external events (Jira tickets, Slack notifications, Support escalation)
for critical, bug, or churn risk feedback. Persists records to agent_action_logs.
"""

import json
import logging
import random
from uuid import UUID

from app.database import async_session_factory
from app.agents.state import FeedbackAgentState
from app.models.agent_run import AgentActionLog

logger = logging.getLogger("app.agents.action")


async def action_node(state: FeedbackAgentState) -> dict:
    """Action Node: evaluates conditions (critical issue, bugs, churn risk) to fire mock Slack/Jira alerts."""
    logger.info("Action Agent evaluating alert rules...")

    feedback_id = state.get("feedback_id")
    category = state.get("category", "other")
    priority = state.get("priority", "low")
    is_churn_risk = state.get("is_churn_risk", False)

    if not feedback_id:
        logger.error("No feedback_id found in agent state.")
        return {}

    actions_triggered = []
    slack_alert_sent = False
    jira_ticket_key = None

    async with async_session_factory() as db:
        try:
            # Rule 1: Slack Alerts (Critical priority or Churn Warning)
            if priority == "critical" or is_churn_risk:
                slack_payload = {
                    "text": f"🚨 *ALERT: Action Required* 🚨\nFeedback ID: {feedback_id}\nPriority: {priority.upper()}\nChurn Risk: {is_churn_risk}\nText snippet: {state.get('raw_text', '')[:100]}..."
                }
                logger.info("Mock Slack Alert dispatched: %s", json.dumps(slack_payload))
                
                # Log action to PostgreSQL
                action_log = AgentActionLog(
                    feedback_id=UUID(feedback_id),
                    action_type="slack_alert",
                    status="success",
                    details=json.dumps(slack_payload),
                )
                db.add(action_log)
                slack_alert_sent = True
                actions_triggered.append("slack_alert")

            # Rule 2: Jira Tickets (Critical / High priority bugs or feature requests)
            if priority in ["critical", "high"] or category in ["bug", "feature"]:
                ticket_num = random.randint(1000, 9999)
                jira_ticket_key = f"FEED-{ticket_num}"
                jira_payload = {
                    "project": "FEED",
                    "summary": f"[{category.upper()}] Customer Feedback issue {jira_ticket_key}",
                    "description": state.get("raw_text", ""),
                    "priority": "Highest" if priority == "critical" else "High" if priority == "high" else "Medium",
                }
                logger.info("Mock Jira Ticket created: key=%s, payload=%s", jira_ticket_key, json.dumps(jira_payload))
                
                # Log action to PostgreSQL
                action_log = AgentActionLog(
                    feedback_id=UUID(feedback_id),
                    action_type="jira_ticket",
                    status="success",
                    details=json.dumps(jira_payload),
                )
                db.add(action_log)
                actions_triggered.append(f"jira_ticket ({jira_ticket_key})")

            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error("Action Agent alert logging failed: %s", str(e))

    logs = state.get("agent_logs", [])
    logs.append(
        f"Action Agent: Dispatched rules (slack_sent={slack_alert_sent}, jira_key={jira_ticket_key}, actions={actions_triggered})"
    )

    return {
        "actions_triggered": actions_triggered,
        "slack_alert_sent": slack_alert_sent,
        "jira_ticket_key": jira_ticket_key,
        "agent_logs": logs,
    }
