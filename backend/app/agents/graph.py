"""
LangGraph compilation module.

Assembles the StateGraph, configures agent node paths, and returns the compiled execution graph.
"""

import logging
from langgraph.graph import StateGraph, END

from app.agents.state import FeedbackAgentState
from app.agents.collector import collector_node
from app.agents.analyzer import analyzer_node
from app.agents.trend import trend_node
from app.agents.action import action_node
from app.agents.learning import learning_node

logger = logging.getLogger("app.agents.graph")

_compiled_graph = None


def get_graph():
    """Build and compile the multi-agent state graph."""
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph

    logger.info("Assembling multi-agent LangGraph workflow...")

    # 1. Initialize State Graph
    workflow = StateGraph(FeedbackAgentState)

    # 2. Add Nodes
    workflow.add_node("collector", collector_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("trend", trend_node)
    workflow.add_node("action", action_node)
    workflow.add_node("learning", learning_node)

    # 3. Add Edges (Collector -> Analyzer -> Trend -> Action -> Learning)
    workflow.add_edge("collector", "analyzer")
    workflow.add_edge("analyzer", "trend")
    workflow.add_edge("trend", "action")
    workflow.add_edge("action", "learning")
    
    # Define end of processing
    workflow.add_edge("learning", END)

    # 4. Set Entry Point
    workflow.set_entry_point("collector")

    # 5. Compile Graph
    _compiled_graph = workflow.compile()
    logger.info("Multi-agent state graph successfully compiled.")
    return _compiled_graph


# Allow executing file directly for local testing
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test_run():
        graph = get_graph()
        initial_state = {
            "raw_text": "The payment system is broken and I lost my data! Please fix ASAP.",
            "rating": 1,
            "source": "web",
            "actions_triggered": [],
            "agent_logs": []
        }
        print("Starting local agent simulation run...")
        result = await graph.ainvoke(initial_state)
        print("\n=== Agent Pipeline Final Output State ===")
        import pprint
        pprint.pprint(result)

    asyncio.run(test_run())
