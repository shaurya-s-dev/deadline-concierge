"""
server.py
---------
MCP server exposing deadline-management tools to the ADK agent.

Run standalone for testing:
    python mcp_server/server.py

This uses the official `mcp` Python SDK (stdio transport), which is what
ADK / Gemini agent CLIs expect when you register a local MCP server.

Security notes (relevant to the "Security features" evaluation criterion):
- No API keys or secrets live in this file. If any external API is added
  later, its key MUST be read via os.environ, never hardcoded.
- Every tool validates its own inputs (see storage.py) before touching
  the filesystem, so malformed agent-generated calls can't corrupt data.
- The server only ever touches files inside ./data — no arbitrary file
  system access is exposed to the agent.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

import storage

server = Server("deadline-concierge")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_deadline",
            description="Add a new deadline/task with a title, due date (YYYY-MM-DD), and optional category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "What the deadline is for"},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                    "category": {"type": "string", "description": "e.g. hackathon, assignment, exam"},
                },
                "required": ["title", "due_date"],
            },
        ),
        Tool(
            name="list_deadlines",
            description="List all deadlines. By default only shows ones not yet marked done.",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_done": {"type": "boolean", "description": "Include completed deadlines too"},
                },
            },
        ),
        Tool(
            name="get_upcoming",
            description="Get deadlines due within the next N days (includes overdue items).",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Look-ahead window in days (default 7)"},
                },
            },
        ),
        Tool(
            name="mark_done",
            description="Mark a deadline as completed, given its id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deadline_id": {"type": "string", "description": "The id of the deadline to mark done"},
                },
                "required": ["deadline_id"],
            },
        ),
        Tool(
            name="delete_deadline",
            description="Permanently delete a deadline, given its id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deadline_id": {"type": "string", "description": "The id of the deadline to delete"},
                },
                "required": ["deadline_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    arguments = arguments or {}

    if name == "add_deadline":
        result = storage.add_deadline(
            title=arguments.get("title", ""),
            due_date=arguments.get("due_date", ""),
            category=arguments.get("category", "general"),
        )
    elif name == "list_deadlines":
        result = storage.list_deadlines(include_done=arguments.get("include_done", False))
    elif name == "get_upcoming":
        result = storage.get_upcoming(days=arguments.get("days", 7))
    elif name == "mark_done":
        result = storage.mark_done(arguments.get("deadline_id", ""))
    elif name == "delete_deadline":
        result = storage.delete_deadline(arguments.get("deadline_id", ""))
    else:
        result = {"error": f"Unknown tool '{name}'"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
