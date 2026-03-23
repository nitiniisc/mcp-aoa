# MCP-based Agent of Agents (AoA)

A minimal but complete **Agent of Agents** system built on the Claude Agent SDK and MCP (Model Context Protocol). An orchestrator agent receives a task, decides which specialist subagent is best suited for it, delegates the work, and streams back the final answer.

---

## What is Agent of Agents (AoA)?

AoA is an architecture pattern where a **single orchestrator agent** manages multiple **specialist subagents**. Instead of one monolithic agent trying to do everything, each subagent is scoped to a narrow capability and is only given the tools it needs. This keeps each agent focused, cheaper to run, and easier to debug.

---

## Architecture Overview

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│        Orchestrator Agent        │
│  (claude-opus-4-6)               │
│                                  │
│  "Which subagent should I use?"  │
│  Decides based on task type      │
└────────────┬────────────────────┘
             │  delegates via Agent tool
     ┌───────┼───────────────┐
     │       │               │
     ▼       ▼               ▼
┌─────────┐ ┌────────────┐ ┌───────────┐
│Researcher│ │ Calculator │ │Summarizer │
│  Agent   │ │   Agent    │ │   Agent   │
└────┬─────┘ └─────┬──────┘ └─────┬─────┘
     │             │               │
     ▼             ▼               ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│search_knowl- │ │   run_   │ │  summarize_  │
│    edge      │ │calculation│ │    text      │
│  WebSearch   │ └──────────┘ └──────────────┘
└──────────────┘
       │
  MCP Server
  (custom-tools)
```

---

## Step-by-Step Flow

### Step 1 — User sends a task

```bash
python main.py "What is MCP?"
```

The task string is passed to the **orchestrator agent** running on `claude-opus-4-6`.

---

### Step 2 — MCP server starts

```
main.py
  └── create_sdk_mcp_server("custom-tools", tools=[...])
```

Before the orchestrator runs, an in-process **MCP server** is spun up exposing three custom tools:

| Tool | Description |
|------|-------------|
| `search_knowledge` | Looks up answers from a local knowledge store |
| `run_calculation` | Evaluates a math expression safely |
| `summarize_text` | Truncates text to a short snippet |

These tools are available to all agents in the session.

---

### Step 3 — Orchestrator decides which subagent to use

The orchestrator reads the system prompt:

> "Delegate the user's task to the most appropriate subagent using the Agent tool."

It picks one of three subagents based on the task type:

| Task type | Subagent chosen |
|-----------|----------------|
| Factual / knowledge question | `researcher` |
| Math expression | `calculator` |
| Text to shorten | `summarizer` |

---

### Step 4 — Subagent executes with scoped tools

The chosen subagent runs in isolation with only its own tools:

**Researcher** (`search_knowledge` + `WebSearch`)
```
"What is MCP?"
  → tries search_knowledge first
  → if not found, falls back to WebSearch
  → returns answer
```

**Calculator** (`run_calculation`)
```
"12 * (3 + 7)"
  → calls run_calculation("12 * (3 + 7)")
  → returns "120"
```

**Summarizer** (`summarize_text`)
```
"The quick brown fox..."
  → calls summarize_text(text)
  → returns first 20 words + "..."
```

---

### Step 5 — Answer streams back to the user

The subagent's response flows back through the orchestrator and is streamed to the terminal token by token via `ClaudeSDKClient.receive_response()`.

```
Orchestrator → AssistantMessage → TextBlock → print(block.text)
```

---

## Project Structure

```
mcp-aoa-tool/
├── main.py          # Entry point — orchestrator agent + MCP server setup
├── agents.py        # Subagent definitions (tools, prompts, descriptions)
├── tools.py         # Custom MCP tool implementations
└── requirements.txt # Dependencies
```

### `main.py`
- Creates the MCP server with all custom tools
- Defines the orchestrator's system prompt and `ClaudeAgentOptions`
- Opens a `ClaudeSDKClient` session, sends the task, streams the response

### `agents.py`
- Defines each subagent as an `AgentDefinition` with:
  - `description` — used by the orchestrator to pick the right agent
  - `prompt` — the subagent's instruction set
  - `tools` — only the tools this subagent needs

### `tools.py`
- Each tool is decorated with `@tool(name, description, schema)`
- Tools are async functions that return `{"content": [{"type": "text", "text": "..."}]}`
- Registered into the MCP server and injected into the agent session

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY=your_key_here
```

---

## Run

```bash
# Knowledge / research question (uses researcher → search_knowledge or WebSearch)
python main.py "What is MCP?"

# Math expression (uses calculator → run_calculation)
python main.py "Calculate 12 * (3 + 7)"

# Summarization (uses summarizer → summarize_text)
python main.py "Summarize: The quick brown fox jumps over the lazy dog many times."

# Web search fallback (researcher hits WebSearch for current info)
python main.py "What is the latest Claude model from Anthropic?"
```

---

## Extending the System

**Add a new tool** — define it in `tools.py` with `@tool`, then add it to the relevant subagent's `tools` list in `agents.py`.

**Add a new subagent** — add a new `AgentDefinition` entry in `agents.py` and update the orchestrator's system prompt in `main.py` to describe when to use it.

**Connect an external MCP server** — add it to `mcp_servers` in `ClaudeAgentOptions`:
```python
mcp_servers={
    "custom": mcp_server,                          # in-process
    "postgres": {"command": "npx", "args": [...]}  # external stdio
}
```
