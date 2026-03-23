# MCP-based Agent of Agents (AoA)

Minimal AoA tool: an orchestrator delegates tasks to specialist subagents via MCP custom tools.

## Structure

```
mcp-aoa-tool/
├── main.py       # Orchestrator entry point
├── agents.py     # Subagent definitions
├── tools.py      # MCP custom tools
└── requirements.txt
```

## Agents

| Agent       | Capability                        |
|-------------|-----------------------------------|
| researcher  | Knowledge base search             |
| calculator  | Math expression evaluation        |
| summarizer  | Text summarization                |

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
```

## Run

```bash
python main.py "What is MCP?"
python main.py "Calculate 12 * (3 + 7)"
python main.py "Summarize: The quick brown fox jumps over the lazy dog."
```
