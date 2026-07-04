"""
agent.py
--------
ADK agent definition for the Deadline Concierge.

This agent is a single-agent ADK setup (not multi-agent) that connects
to our local MCP server (mcp_server/server.py) to manage deadlines
through natural conversation, e.g.:

    "Add my Alphaline hackathon deadline for June 30"
    "What's due in the next 3 days?"
    "Mark the OODP assignment as done"

Security notes:
- GEMINI_API_KEY / GOOGLE_API_KEY is read from the environment only.
  Never hardcode it here. See .env.example for the expected variable name.
- The MCP server subprocess only has access to ./data — the agent has
  no direct filesystem or shell access itself.
"""

import os
import sys
from datetime import date
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Fail fast with a clear message instead of a cryptic auth error later.
if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
    print(
        "WARNING: GOOGLE_API_KEY / GEMINI_API_KEY not set in environment. "
        "Set it in a .env file or export it before running the agent.",
        file=sys.stderr,
    )

MCP_SERVER_PATH = str(Path(__file__).resolve().parent.parent / "mcp_server" / "server.py")

deadline_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=[MCP_SERVER_PATH],
    )
)

root_agent = Agent(
    name="deadline_concierge",
    model="gemini-2.5-flash-lite",
    description="A personal concierge agent that tracks hackathon, assignment, and exam deadlines.",
    instruction=(
        f"Today's date is {date.today().isoformat()}. Always use this as 'today' when reasoning "
        "about dates — never assume a different year.\n\n"
        "You are a friendly, efficient deadline-tracking concierge for a college student "
        "juggling multiple hackathons, assignments, and exams.\n\n"
        "Guidelines:\n"
        "- When the user mentions a task with a date, use add_deadline to save it. "
        "Infer a sensible category (hackathon, assignment, exam, general) if not stated.\n"
        "- Always convert dates to YYYY-MM-DD before calling a tool. If the year is missing, "
        "assume the current year (given above) unless that date has already passed relative to "
        "today, in which case assume next year.\n"
        "- When asked what's due soon, use get_upcoming and summarize clearly, flagging anything "
        "overdue (negative days_remaining) prominently.\n"
        "- When asked to see everything, use list_deadlines.\n"
        "- When the user says something is done/finished/submitted, find the matching deadline "
        "(list_deadlines first if you don't have the id) and call mark_done.\n"
        "- Be concise. Use short bullet points for lists of deadlines, not long prose.\n"
        "- Never invent deadlines the user didn't mention. Never expose internal ids unless useful "
        "for disambiguation."
    ),
    tools=[deadline_tools],
)
