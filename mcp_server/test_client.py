"""
test_client.py
---------------
Standalone smoke test that connects to server.py as a real MCP client
would (over stdio), lists tools, and calls a couple of them.

Run:
    python mcp_server/test_client.py

This does NOT require a Gemini API key — it only tests the MCP layer,
not the ADK agent.
"""

import asyncio
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = str(Path(__file__).resolve().parent / "server.py")


async def main():
    params = StdioServerParameters(command="python3", args=[SERVER_PATH])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            print("\n--- add_deadline ---")
            result = await session.call_tool(
                "add_deadline",
                {"title": "Test Hackathon Submission", "due_date": "2026-07-06", "category": "hackathon"},
            )
            print(result.content[0].text)

            print("\n--- list_deadlines ---")
            result = await session.call_tool("list_deadlines", {})
            print(result.content[0].text)

            print("\n--- get_upcoming ---")
            result = await session.call_tool("get_upcoming", {"days": 30})
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
