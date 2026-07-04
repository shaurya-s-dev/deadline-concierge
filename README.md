# Deadline Concierge

A personal AI concierge agent that helps students track hackathon, assignment, and exam deadlines through natural conversation — built for the **AI Agents: Intensive Vibe Coding Capstone Project** (Concierge Agents track).

## Problem

Students juggling multiple hackathons, coursework, and exams end up tracking deadlines across scattered notes, chat threads, and memory. Missed or forgotten deadlines are a real, everyday cost — and most task-tracking apps require manual data entry through forms rather than just *telling* something what's due.

## Solution

Deadline Concierge is a conversational agent you talk to naturally:

- "Add my Alphaline hackathon deadline for June 30"
- "What's due in the next 3 days?"
- "Mark the OODP assignment as done"

The agent interprets these requests, calls the right tool, and keeps all data **stored locally** — nothing leaves the user's machine, which matters for a Concierge agent handling personal schedule information.

## Architecture

```
┌─────────────────────┐
│   User (CLI chat)    │
└──────────┬───────────┘
           │ natural language
           ▼
┌─────────────────────┐
│  ADK Agent           │  (Gemini 2.0 Flash)
│  agent/agent.py       │  - interprets intent
│                       │  - normalizes dates
└──────────┬───────────┘
           │ MCP protocol (stdio)
           ▼
┌─────────────────────┐
│  MCP Server           │
│  mcp_server/server.py │  exposes 5 tools:
│                       │   add_deadline, list_deadlines,
│                       │   get_upcoming, mark_done, delete_deadline
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│  Local JSON store     │
│  data/deadlines.json  │  (never leaves the machine)
└─────────────────────┘
```

**Why this design:**
- **Single ADK agent, not multi-agent** — the task is simple enough that a multi-agent split would add complexity without adding value. All conceptual "reasoning" (date normalization, tone, prioritization) lives in the agent's instructions.
- **MCP server as the tool boundary** — keeps agent logic and data logic cleanly separated, and makes the tools reusable by any other MCP-compatible client, not just this agent.
- **Local file storage** — no cloud DB, no external API calls beyond Gemini itself. This was a deliberate choice to keep personal deadline data private.

## Course concepts demonstrated

| Concept | Where |
|---|---|
| Agent (ADK) | `agent/agent.py` — single ADK `Agent` with tool-calling instructions |
| MCP Server | `mcp_server/server.py` — full MCP server with 5 registered tools |
| Security features | Env-var-only API keys (`.env`, never committed), input validation in `storage.py`, no external network access from the MCP server, `.gitignore` for secrets and data |

## Setup

```bash
git clone <your-repo-url>
cd deadline-concierge
pip install -r requirements.txt
cp .env.example .env   # then paste your Gemini API key into .env
python run_cli.py
```

### Testing the MCP server standalone (no API key needed)

```bash
python mcp_server/test_client.py
```

This connects to the MCP server exactly as the agent would, lists all tools, and exercises `add_deadline`, `list_deadlines`, and `get_upcoming`.

## Project structure

```
deadline-concierge/
├── agent/
│   ├── __init__.py
│   └── agent.py           # ADK agent definition
├── mcp_server/
│   ├── server.py           # MCP server (5 tools)
│   ├── storage.py          # Validation + local JSON persistence
│   └── test_client.py      # Standalone MCP smoke test
├── data/
│   └── deadlines.json      # Created automatically at runtime (gitignored)
├── run_cli.py              # Terminal chat interface
├── requirements.txt
├── .env.example
└── .gitignore
```

## Security notes

- API keys are read exclusively from environment variables (`GOOGLE_API_KEY` / `GEMINI_API_KEY`), never hardcoded.
- `.env` and `data/deadlines.json` are gitignored so no secrets or personal data are ever committed.
- All tool inputs are validated in `storage.py` (date format, title length/emptiness) before touching the filesystem.
- The MCP server can only read/write inside `./data` — it has no access to the wider filesystem or shell.

## License

CC-BY 4.0 (per competition rules).
