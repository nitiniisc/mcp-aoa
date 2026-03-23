"""
MCP-based Agent of Agents (AoA) — minimal example.

Orchestrator receives a task, decides which subagent to delegate to,
and returns the final answer.

Usage:
    python main.py "What is MCP?"
    python main.py "Calculate 12 * (3 + 7)"
    python main.py "Summarize: The quick brown fox jumps over the lazy dog many times."
"""

import sys
import anyio

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
)

from tools import search_knowledge, run_calculation, summarize_text
from agents import AGENTS

SYSTEM_PROMPT = """You are an orchestrator agent. You have three specialist subagents:
- researcher  → factual / knowledge questions
- calculator  → math expressions
- summarizer  → text summarization

Delegate the user's task to the most appropriate subagent using the Agent tool.
Return the subagent's answer directly."""


async def run(task: str) -> str:
    mcp_server = create_sdk_mcp_server(
        "custom-tools",
        tools=[search_knowledge, run_calculation, summarize_text],
    )

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=["Agent"],
        agents=AGENTS,
        mcp_servers={"custom": mcp_server},
        permission_mode="bypassPermissions",
        max_turns=10,
        model="claude-opus-4-6",
    )

    result = ""
    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
                        result += block.text
            elif isinstance(msg, ResultMessage):
                if msg.result and not result:
                    result = msg.result
    return result


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or "What is AoA (Agent of Agents)?"
    print(f"Task: {task}\n---\n")
    anyio.run(run, task)
    print("\n---\nDone.")
