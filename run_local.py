#!/usr/bin/env python3
import asyncio
import os
import sys

from google.adk.runners import Runner
from google.genai import types

# Add local directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent import app as adk_app
from app.app_utils import services


async def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello! What can you help me with?"
    user_id = sys.argv[2] if len(sys.argv) > 2 else "founder-1"
    session_id = sys.argv[3] if len(sys.argv) > 3 else "session-1"

    print(f"\n🗣️ User Query: {prompt}")
    print("-" * 50)

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        memory_service=services.get_memory_service(),
        auto_create_session=True,
    )

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )

    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    )

    for event in events:
        if hasattr(event, "content") and event.content:
            for part in getattr(event.content, "parts", []):
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    print(f"\n🛠️ Tool Call: {fc.name}({fc.args})")
                elif hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    print(f"\n📥 Tool Response: {fr.response}")
                elif hasattr(part, "text") and part.text:
                    print(f"\n🤖 Agent:\n{part.text}")


if __name__ == "__main__":
    asyncio.run(main())
