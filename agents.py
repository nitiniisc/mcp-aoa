"""Subagent definitions for the AoA orchestrator."""

from claude_agent_sdk import AgentDefinition

AGENTS = {
    "researcher": AgentDefinition(
        description="Searches the knowledge base and answers factual questions.",
        prompt="You are a research assistant. Use the search_knowledge tool to find information and return a clear answer.",
        tools=["search_knowledge"],
    ),
    "calculator": AgentDefinition(
        description="Evaluates mathematical expressions and returns the result.",
        prompt="You are a math assistant. Use the run_calculation tool to evaluate expressions.",
        tools=["run_calculation"],
    ),
    "summarizer": AgentDefinition(
        description="Summarizes provided text into a short snippet.",
        prompt="You are a summarization assistant. Use the summarize_text tool to create a brief summary.",
        tools=["summarize_text"],
    ),
}
