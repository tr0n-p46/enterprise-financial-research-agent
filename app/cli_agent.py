"""
Minimal CLI entry point for the Enterprise Financial Research Agent.

This is a deliberately thin, throwaway-quality script whose only purpose
is to prove the core Agno + Groq + tool-calling loop works end to end.
No architecture, no abstractions — that comes in later milestones once
this foundation is verified to actually function.
"""

import os

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

# Load variables from .env into the process environment.
# Must happen before we read os.environ below.
load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID", "llama-3.3-70b-versatile")


def build_agent() -> Agent:
    """Construct a minimal single-tool research agent.

    Returns:
        An Agno Agent configured with a Groq-hosted model and DuckDuckGo
        web search as its only tool.
    """
    return Agent(
        model=Groq(id=GROQ_MODEL_ID, api_key=GROQ_API_KEY),
        description=(
            "You are a financial research assistant. You answer questions "
            "using current, verifiable information rather than guessing."
        ),
        tools=[DuckDuckGoTools()],
        show_tool_calls=True,
        markdown=True,
    )


if __name__ == "__main__":
    agent = build_agent()
    agent.print_response(
        "What's the latest news on Nvidia stock?",
        stream=True,
    )