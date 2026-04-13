from google.adk.tools.tool_context import ToolContext


def save_research(topic: str, results: str, tool_context: ToolContext) -> dict:
    """Save a completed research result to the session state.

    Args:
        topic: The research topic or query
        results: The research findings/summary returned to the user
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(f"--- Tool: save_research called for '{topic}' ---")

    research_history = tool_context.state.get("research_history", [])
    entry = {"topic": topic, "results": results}
    research_history.append(entry)
    tool_context.state["research_history"] = research_history

    return {
        "action": "save_research",
        "topic": topic,
        "message": f"Saved research on: {topic}",
    }


def view_research_history(tool_context: ToolContext) -> dict:
    """View all past research topics and results.

    Args:
        tool_context: Context for accessing session state

    Returns:
        The list of past research entries
    """
    print("--- Tool: view_research_history called ---")

    research_history = tool_context.state.get("research_history", [])

    return {
        "action": "view_research_history",
        "research_history": research_history,
        "count": len(research_history),
    }
