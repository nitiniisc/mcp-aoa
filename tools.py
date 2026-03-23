"""Custom MCP tools exposed to all agents."""

from claude_agent_sdk import tool


@tool("search_knowledge", "Search a knowledge base for information", {"query": str})
async def search_knowledge(args):
    query = args["query"]
    # Stub: replace with real DB/search call
    results = {
        "python": "Python is a high-level, interpreted programming language.",
        "mcp": "MCP (Model Context Protocol) enables agents to use external tools.",
        "aoa": "Agent of Agents (AoA) is a pattern where an orchestrator delegates to subagents.",
    }
    answer = next((v for k, v in results.items() if k in query.lower()), "No results found.")
    return {"content": [{"type": "text", "text": answer}]}


@tool("run_calculation", "Evaluate a simple math expression", {"expression": str})
async def run_calculation(args):
    try:
        result = eval(args["expression"], {"__builtins__": {}})  # noqa: S307 — restricted eval
        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool("summarize_text", "Return a short summary stub for given text", {"text": str})
async def summarize_text(args):
    words = args["text"].split()
    summary = " ".join(words[:20]) + ("..." if len(words) > 20 else "")
    return {"content": [{"type": "text", "text": summary}]}
