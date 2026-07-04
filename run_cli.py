"""
run_cli.py
----------
Minimal terminal chat loop for demoing the Deadline Concierge agent.

Usage:
    1. cp .env.example .env   (then fill in your GOOGLE_API_KEY)
    2. pip install -r requirements.txt
    3. python run_cli.py

Type 'exit' or Ctrl+C to quit.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from agent.agent import root_agent

APP_NAME = "deadline_concierge_cli"
USER_ID = "local_user"


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

    print("Deadline Concierge — type 'exit' to quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if not user_input:
            continue

        content = types.Content(role="user", parts=[types.Part(text=user_input)])

        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent: {part.text}")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("Set GOOGLE_API_KEY in a .env file first (see .env.example).")
    else:
        asyncio.run(main())
